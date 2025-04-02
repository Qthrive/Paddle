from flask import Flask,render_template,request,flash,redirect,url_for,jsonify
import os
import subprocess
import uuid
from werkzeug.utils import secure_filename

pingpong = Flask(__name__, static_url_path='/static', static_folder='static')
pingpong.secret_key = '121212'

# 处理图片的配置
UPLOAD_FOLDER = 'static/uploads'
PROCESSED_FOLDER = 'static/processed'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov'}

pingpong.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
pingpong.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# 确保目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 装饰器，用于告诉 Flask 哪个 URL 应该触发下面的函数。在这个例子中，它指定了根 URL（即网站的主页）。
@pingpong.route("/") 
def show_login():
    # return render_template('login.html')
    return render_template('dashboard.html')

@pingpong.route("/login",methods = ['POST'])
def login():
    # while True:
    username = request.form.get('username')
    password = request.form.get('password')
    if username == 'admin' and password == '111222':
        return redirect(url_for('dashboard'))
    else:
        flash('用户名或密码错误，请重试','error')
        return redirect(url_for('show_login'))
    
@pingpong.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

@pingpong.route('/predict_img', methods=['POST'])
def predict_img():
    # 检查是否有文件上传
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    # 保存上传文件
    filename = secure_filename(file.filename)
    input_path = os.path.join(pingpong.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)
    
    try:
        # 第一阶段检测
        det_output_dir = os.path.join(PROCESSED_FOLDER, 'detection')
        os.makedirs(det_output_dir, exist_ok=True)
        det_cmd = [
            'python', 'E:/pingpong_train_data/PaddleDetection/tools/infer.py',
            '-c', 'E:/pingpong_train_data/PaddleDetection/configs/picodet/ppq.yml',
            '--infer_img', input_path,
            '-o', 'weights="E:/pingpong_train_data/PaddleDetection/output/ppq/best_model.pdopt"',
            '--output_dir', det_output_dir
        ]
        subprocess.run(det_cmd, check=True)
        
        # 第二阶段关键点检测
        kp_output_dir = os.path.join(PROCESSED_FOLDER, 'keypoint')
        os.makedirs(kp_output_dir, exist_ok=True)
        kp_cmd = [
            'python', 'E:/pingpong_train_data/PaddleDetection/deploy/python/det_keypoint_unite_infer.py',
            '--det_model_dir', 'models/detection/picodet_v2_s_320_pedestrian',
            '--keypoint_model_dir', 'models/keypoint/tinypose_128x96',
            '--image_dir', det_output_dir,
            '--device', 'GPU',
            '--output_dir', kp_output_dir
        ]
        subprocess.run(kp_cmd, check=True)
        
        
        return jsonify({
            'original': url_for('static', filename=f'uploads/{filename}'),
            'processed': url_for('static', filename=f'processed/keypoint/{filename.replace(r".png",r"_vis_vis.jpg")}'),
        })
        
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500
    finally:
        # 清理临时文件（可选）
        pass

@pingpong.route('/predict_video', methods=['POST'])
def predict_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    # 生成唯一标识符
    task_id = str(uuid.uuid4())
    video_dir = os.path.join(PROCESSED_FOLDER, 'video', task_id)
    os.makedirs(video_dir, exist_ok=True)
    
    # 保存原始视频
    filename = secure_filename(file.filename)
    input_path = os.path.join(video_dir, filename)
    file.save(input_path)
    
    try:
        # 1. 拆分视频为帧
        frame_dir = os.path.join(video_dir, 'frames')
        os.makedirs(frame_dir, exist_ok=True)
        split_cmd = [
            'ffmpeg', '-i', input_path, 
            '-vf', 'fps=30',  # 保持与原视频相同帧率
            os.path.join(frame_dir, 'frame_%05d.png')
        ]
        subprocess.run(split_cmd, check=True)
        
        # 2. 目标检测处理
        det_dir = os.path.join(video_dir, 'detected')
        os.makedirs(det_dir, exist_ok=True)
        det_cmd = [
            'python', 'E:/pingpong_train_data/PaddleDetection/tools/infer.py',
            '-c', 'E:/pingpong_train_data/PaddleDetection/configs/picodet/ppq.yml',
            '--infer_dir', frame_dir,
            '-o', 'weights=E:/pingpong_train_data/PaddleDetection/output/ppq/best_model.pdopt',
            '--output_dir', det_dir
        ]
        subprocess.run(det_cmd, check=True)
        
        # 3. 关键点检测处理
        kp_dir = os.path.join(video_dir, 'keypoints')
        os.makedirs(kp_dir, exist_ok=True)
        kp_cmd = [
            'python', 'E:/pingpong_train_data/PaddleDetection/deploy/python/det_keypoint_unite_infer.py',
            '--det_model_dir', 'models/detection/picodet_v2_s_320_pedestrian',
            '--keypoint_model_dir', 'models/keypoint/tinypose_128x96',
            '--image_dir', det_dir,
            '--device', 'GPU',
            '--output_dir', kp_dir
        ]
        subprocess.run(kp_cmd, check=True)
        
        # 4. 合成视频
        output_video = os.path.join(video_dir, 'processed_' + filename)
        synthesize_cmd = [
            'ffmpeg', '-framerate', '30',  # 与拆分时帧率一致
            '-i', os.path.join(kp_dir, 'frame_%05d_vis_vis.jpg'),
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
            output_video
        ]
        subprocess.run(synthesize_cmd, check=True)
        
        return jsonify({
            'original': url_for('static', filename=f'uploads/{filename}'),
            'processed': url_for('static', filename=f'processed/video/{task_id}/processed_{filename}')
        })
        
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'处理失败: {str(e)}'}), 500

if __name__ == "__main__":
    pingpong.run(debug=True)