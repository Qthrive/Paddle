import json

# 读取原始标注文件
with open(r"E:\pingpong_train_data\train_part1\game_2\annotations.json", 'r') as f:
    original_data = json.load(f)

# 转换为COCO格式
coco_data = {
    "images": [],
    "annotations": [],
    "categories": [{"id": 1, "name": "ball"}]
}

for img_id, info in original_data.items():
    if not img_id.isdigit():
        continue
        
    img_id = int(img_id)
    filename = f"frame_{img_id:06d}.png"
    
    coco_data["images"].append({
        "id": img_id,
        "file_name": filename,
        "width": 1920,  # 根据实际情况修改
        "height": 1080
    })
    
    if "ball_position" in info:
        coco_data["annotations"].append({
            "id": len(coco_data["annotations"]) + 1,
            "image_id": img_id,
            "category_id": 1,
            "bbox": [
                info["ball_position"]["x"],
                info["ball_position"]["y"],
                10, 10  # 假设球的直径为10像素
            ],
            "area": 100,
            "iscrowd": 0
        })

# 保存新标注文件
with open(r"E:\pingpong_train_data\train_part1\game_2\coco_annotations.json", 'w') as f:
    json.dump(coco_data, f)