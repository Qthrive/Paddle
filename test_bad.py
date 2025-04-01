import os
from PIL import Image

def check_images(folder):
    corrupted = []
    for fname in os.listdir(folder):
        if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                img_path = os.path.join(folder, fname)
                # 尝试打开并验证图片
                with Image.open(img_path) as img:
                    img.verify()  # 验证文件完整性
            except Exception as e:
                print(f"损坏文件: {fname}, 错误: {str(e)}")
                corrupted.append(fname)
    return corrupted

# 使用示例
folder = r"E:\pingpong_train_data\train_part1\game_1\frames"
corrupted_files = check_images(folder)
print(f"共发现 {len(corrupted_files)} 个损坏文件：", corrupted_files)

