# detector/urls.py
from django.urls import path
from . import views  # 导入当前应用的视图

urlpatterns = [
    # 上传图片的接口
    path('upload/', views.UploadImageView.as_view(), name='upload_image'),
]