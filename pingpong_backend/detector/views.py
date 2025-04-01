from django.shortcuts import render

# Create your views here.
# detector/views.py
import subprocess
import os
import json
from django.http import JsonResponse
from django.views import View
from django.core.files.storage import default_storage
from django.conf import settings
from .models import UploadedImage, DetectionResult
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')  # 跳过 CSRF 验证

class UploadImageView(View):
    def post(self, request):
        # 1. 保存上传的图片
        uploaded_file = request.FILES['image']
        file_name = default_storage.save('uploads/' + uploaded_file.name, uploaded_file)
        input_path = default_storage.path(file_name)
        output_dir = os.path.join(settings.MEDIA_ROOT, 'processed', os.path.splitext(file_name)[0])
        
        # 2. 运行目标检测模型
        try:
            subprocess.run([
                "python", "E:/pingpong_train_data/PaddleDetection/tools/infer.py",
                "-c", "E:/pingpong_train_data/PaddleDetection/configs/picodet/ppq.yml",
                "--infer_img", input_path.replace("\\", "/"),  # 单张图片用 --image_file
                "-o", "weights=E:/pingpong_train_data/PaddleDetection/output/ppq/best_model.pdopt",
                "--output_dir", output_dir.replace("\\", "/")
            ], check=True)
        except subprocess.CalledProcessError as e:
            return JsonResponse({"error": "目标检测失败", "details": str(e)}, status=500)

        # 3. 运行姿态估计模型（输入为目标检测的输出图片）
        try:
            subprocess.run([
                "python", "E:/pingpong_train_data/PaddleDetection/deploy/python/det_keypoint_unite_infer.py",
                "--det_model_dir", "E:/pingpong_train_data/models/picodet_v2_s_320_pedestrian",
                "--keypoint_model_dir", "E:/pingpong_train_data/models/tinypose_128x96",
                "--image_dir", output_dir,  # 输入目录（含检测结果图片）
                "--device", "GPU",
                "--output_dir", os.path.join(output_dir, "keypoints")
            ], check=True)
        except subprocess.CalledProcessError as e:
            return JsonResponse({"error": "姿态估计失败", "details": str(e)}, status=500)

        # 4. 解析结果并保存到数据库
        result_image_path = os.path.join(output_dir, "keypoints", os.path.basename(input_path))
        result_json_path = os.path.join(output_dir, "keypoints", os.path.splitext(os.path.basename(input_path))[0] + ".json")
        
        # 读取检测结果（示例，需根据实际输出格式调整）
        with open(result_json_path, 'r') as f:
            result_data = json.load(f)
        
        # 保存到数据库
        image_obj = UploadedImage.objects.create(image=file_name)
        DetectionResult.objects.create(
            image=image_obj,
            ball_bbox=result_data.get('ball_bbox'),
            player_bbox=result_data.get('person_bbox'),
            keypoints=result_data.get('keypoints'),
            result_image=result_image_path.replace(str(settings.MEDIA_ROOT), '')  # 保存相对路径
        )

        return JsonResponse({
            "status": "success",
            "result_image": result_image_path,
            "result_data": result_data
        })