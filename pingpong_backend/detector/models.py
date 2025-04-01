from django.db import models

# Create your models here.

class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

class DetectionResult(models.Model):
    image = models.OneToOneField(UploadedImage, on_delete=models.CASCADE)
    ball_bbox = models.JSONField(null=True)  # 乒乓球坐标
    player_bbox = models.JSONField(null=True)  # 运动员框选坐标
    keypoints = models.JSONField(null=True)  # 肢体关键点
    result_image = models.ImageField(upload_to='results/', null=True)