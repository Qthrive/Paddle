import cv2
import os
import re

def multi_game_images_to_video(image_root, output_folder, fps=30):
    # 创建输出目录
    os.makedirs(output_folder, exist_ok=True)
    
    # 遍历所有场次目录
    for game_dir in os.listdir(image_root):
        game_match = re.match(r"game_(\d+)", game_dir)
        if not game_match:
            continue
        
        game_id = int(game_match.group(1))
        game_path = os.path.join(image_root, game_dir, "frames")
        
        # 收集当前场次的所有帧
        images = []
        for filename in os.listdir(game_path):
            frame_match = re.match(r"frame_(\d+)\.png", filename)
            if frame_match:
                frame_num = int(frame_match.group(1))
                images.append( (frame_num, filename) )
        
        # 按帧序号排序
        images = sorted(images, key=lambda x: x[0])
        images = [img[1] for img in images]
        
        # 生成视频
        output_video = os.path.join(output_folder, f"game_{game_id:02d}.mp4")
        create_video(game_path, output_video, images, fps)

def create_video(image_dir, output_video, images, fps):
    # 读取第一张图片获取尺寸
    first_image = cv2.imread(os.path.join(image_dir, images[0]))
    height, width, _ = first_image.shape
    
    # 创建视频写入对象
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
    
    # 逐帧写入视频
    for image_name in images:
        img_path = os.path.join(image_dir, image_name)
        frame = cv2.imread(img_path)
        video_writer.write(frame)
    
    video_writer.release()
    print(f"视频已生成: {output_video}")

# 使用示例
multi_game_images_to_video(
    image_root=r"E:\pingpong_train_data\train_part1",
    output_folder=r"E:\pingpong_train_data\game_videos",
    fps=25  # 25或30帧率
)