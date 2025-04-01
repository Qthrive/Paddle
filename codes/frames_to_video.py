import cv2
import os
import re
from tqdm import tqdm  # 新增进度条库

def create_video_from_images(folder_path, output_path='output.mp4', fps=30):
    # 获取所有图片文件并按数字排序
    def numerical_sort(value):
        numbers = re.findall(r'\d+', value)
        return int(numbers[0]) if numbers else 0

    # 获取所有.jpg或者.png文件并排序
    # images = [f for f in os.listdir(folder_path) if f.lower().endswith('.jpg')]
    images = [f for f in os.listdir(folder_path) if f.lower().endswith('.png')]
    images.sort(key=numerical_sort)

    if not images:
        print("没有找到图片文件")
        return

    # 读取第一张图片获取尺寸
    first_image_path = os.path.join(folder_path, images[0])
    frame = cv2.imread(first_image_path)
    height, width, layers = frame.shape

    # 创建视频写入对象
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # 使用tqdm创建进度条
    with tqdm(total=len(images), unit='帧', desc='处理进度', ncols=100) as pbar:
        for idx, image_name in enumerate(images):
            image_path = os.path.join(folder_path, image_name)
            img = cv2.imread(image_path)
            
            if img is None:
                print(f"\n警告：无法读取 {image_name}，已跳过")
                pbar.update(1)  # 即使失败也更新进度条
                continue
                
            video.write(img)
            # 更新进度条描述（显示当前处理的文件名）
            pbar.set_description(f"处理: {image_name[:20]}")
            pbar.update(1)
            
            # 每处理10帧刷新一次显示（可选）
            if idx % 10 == 0:
                pbar.refresh()

    video.release()
    print(f"\n视频已保存至: {output_path}")

# 使用示例
if __name__ == "__main__":
    # folder_path = r'E:\pingpong_train_data\ooutput'
    # create_video_from_images(folder_path, output_path=r'E:\pingpong_train_data\video\game_2.mp4', fps=30)
    folder_path = r'E:\pingpong_train_data\my_data_collection\ppq_frames'
    create_video_from_images(folder_path, output_path=r'E:\pingpong_train_data\my_data_collection\output_video\ppq_video.mp4', fps=30)