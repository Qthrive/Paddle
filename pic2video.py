import cv2
import os
import re

def multi_game_images_to_video(image_folder, output_folder, fps=30):
    # 创建输出目录
    os.makedirs(output_folder, exist_ok=True)
    
    # 获取所有图片并按游戏场次分组
    game_dict = {}
    for filename in os.listdir(image_folder):
        if filename.endswith(".jpg"):
            # 提取游戏场次和帧序号
            match = re.match(r"game_(\d+)_frame_(\d+)_vis\.jpg", filename)
            if not match:
                continue
                
            game_id = int(match.group(1))
            frame_num = int(match.group(2))
            
            # 按场次分组
            if game_id not in game_dict:
                game_dict[game_id] = []
            game_dict[game_id].append((frame_num, filename))
    
    # 处理每个场次
    for game_id in sorted(game_dict.keys()):
        # 按帧序号排序
        images = sorted(game_dict[game_id], key=lambda x: x[0])
        images = [img[1] for img in images]
        
        # 生成视频
        output_video = os.path.join(output_folder, f"game_{game_id:02d}.mp4")
        create_video(image_folder, output_video, images, fps)

def create_video(image_folder, output_video, images, fps):
    # 读取第一张图片获取尺寸
    first_image = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, _ = first_image.shape
    
    # 创建视频写入对象
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
    
    # 逐帧写入视频
    for image_name in images:
        img_path = os.path.join(image_folder, image_name)
        frame = cv2.imread(img_path)
        video_writer.write(frame)
    
    video_writer.release()
    print(f"视频已生成: {output_video}")

# 使用示例
multi_game_images_to_video(
    image_folder=r"E:\pingpong_train_data\ooutput",
    output_folder=r"E:\pingpong_train_data\game_videos",
    fps=1
)