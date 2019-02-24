from django.db import models


# Create your models here.
class VideoInfo(models.Model):
    video_path = models.CharField(max_length=200, unique=True)
    video_name = models.CharField(max_length=50)
