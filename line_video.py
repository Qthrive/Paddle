import cv2
import os
import re
import json

def create_video_with_trajectory(
    image_folder,
    annotation_path,
    output_path='output_trajectory.mp4',
    fps=30
):
    # 定义球台边界坐标
    LEFT_BOUNDARY_POINTS = [(620, 618), (459, 722)]
    RIGHT_BOUNDARY_POINTS = [(1382, 637), (1535, 752)]

    # 计算直线方程
    def calculate_line_equation(p1, p2):
        A = p2[1] - p1[1]
        B = p1[0] - p2[0]
        C = p2[0]*p1[1] - p1[0]*p2[1]
        return A, B, -C

    # 判断点在直线的哪一侧
    def get_line_side(line, point):
        return (line[0]*point[0] + line[1]*point[1] + line[2]) > 0

    # 初始化边界直线
    left_line = calculate_line_equation(*LEFT_BOUNDARY_POINTS)
    right_line = calculate_line_equation(*RIGHT_BOUNDARY_POINTS)

    # 读取标注文件
    with open(annotation_path, 'r') as f:
        annotations = json.load(f)
    
    # 获取所有图片并排序
    images = [f for f in os.listdir(image_folder) if f.lower().endswith('.jpg')]
    images.sort(key=lambda x: int(re.findall(r'\d+', x)[0].lstrip('0') or 0))  # 支持前导零
    
    # 创建视频写入对象
    first_frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, _ = first_frame.shape
    video = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    
    # 轨迹存储
    trajectory = []
    previous_side = None

    for idx, image_name in enumerate(images):
        # 提取帧号（兼容前导零）
        frame_num = re.findall(r'\d+', image_name)[0].lstrip('0') or '0'
        
        # 获取标注
        current_anno = annotations.get(frame_num, {})
        ball_pos = current_anno.get('ball_position', None)
        
        # 处理球位置
        if ball_pos:

            x, y = ball_pos['x'], ball_pos['y']

            # 检查坐标有效性
            if x < 0 or x >= width or y < 0 or y >= height:
                print('因为负坐标清除')
                trajectory = []
                continue

            print(f"帧 {frame_num} 检测到球坐标: ({x}, {y})")  # 调试信息
            
            # 判断当前区域
            left_side = get_line_side(left_line, (x, y))
            right_side = get_line_side(right_line, (x, y))
            
            # 根据实际边界方向调整判断逻辑（可能需要交换条件）
            if left_side and right_side:
                current_side = 'left'
            elif not left_side and not right_side:
                current_side = 'right'
            else:
                current_side = 'unknown'
            
            # 区域切换时清空轨迹
            if previous_side and current_side != previous_side:
                print(f"检测到区域切换：{previous_side} → {current_side}")  # 调试信息
                trajectory = []
            
            # 添加轨迹点
            trajectory.append((x, y))
            previous_side = current_side
            
            # 限制轨迹长度
            if len(trajectory) > 40:  # 增加保留点数
                trajectory.pop(0)
        else:
            print('因为无坐标清除')
            trajectory = []
            previous_side = None
        
        # 绘制当前帧
        frame = cv2.imread(os.path.join(image_folder, image_name))
        
        # 绘制球台边界
        cv2.line(frame, LEFT_BOUNDARY_POINTS[0], LEFT_BOUNDARY_POINTS[1], (0, 255, 0), 2)
        cv2.line(frame, RIGHT_BOUNDARY_POINTS[0], RIGHT_BOUNDARY_POINTS[1], (0, 255, 0), 2)
        
        # 绘制轨迹（使用更明显的颜色）
        for i in range(1, len(trajectory)):
            cv2.line(frame, trajectory[i-1], trajectory[i], (0, 0, 255), 5)  # 改为红色粗线
        
        # 写入视频
        video.write(frame)
        print(f"\r处理进度: {idx+1}/{len(images)} 帧", end='')
    
    video.release()
    print(f"\n视频已保存至: {output_path}")

# 使用示例
create_video_with_trajectory(
    image_folder=r'E:\pingpong_train_data\ooutput',
    annotation_path=r'E:\pingpong_train_data\train_part1\game_2\annotations.json',
    output_path=r'E:\pingpong_train_data\final_videos\pingpong_trajectory_changed.mp4'
)