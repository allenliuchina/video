from django.shortcuts import render, redirect
from video.settings import BASE_DIR
import re
import os
from wsgiref.util import FileWrapper
from django.http import StreamingHttpResponse
from .tasks import generate_cover
from .models import VideoInfo
from django.core.paginator import Paginator
from django.conf import settings
import shutil


def add_video_path(request):
    if request.method == 'GET':
        return render(request, 'no_video.html', {'delete': True})
    path = request.POST.get('path')
    print(path)
    add_path(path)
    return render(request, 'alert.html', {'alert': '视频正在生成封面中，耐心等待'})


def add_path(video_path):
    # 如果该路径是文件夹，则递归调用
    if os.path.isdir(video_path):
        videos = os.listdir(video_path)
        for video in videos:
            add_path(os.path.join(video_path, video))
    else:
        file_path, file_ext = os.path.splitext(video_path)
        if file_ext.lower() in settings.VIDEOS_EXT:
            file_dir, file_name = os.path.split(file_path)
            try:
                video_info = VideoInfo()
                video_info.video_name = file_name
                video_info.video_path = video_path
                video_info.save()
                generate_cover.delay(video_path)
            except Exception:
                pass


def index(request):
    videos = VideoInfo.objects.order_by('id').all()
    if not videos:
        return redirect('main:add')
    paginator = Paginator(videos, 12)
    page_get = request.GET.get('p')
    if not page_get:
        page_get = 1
    videos_page = paginator.page(int(page_get))

    return render(request, 'index.html', {'files': videos_page, 'page': paginator})


def detail(request, id):
    return render(request, 'play.html', {'id': id})


def file_iterator(file_name, chunk_size=8192, offset=0, length=None):
    with open(file_name, "rb") as f:
        f.seek(offset, os.SEEK_SET)
        remaining = length
        while True:
            bytes_length = chunk_size if remaining is None else min(remaining, chunk_size)
            data = f.read(bytes_length)
            if not data:
                break
            if remaining:
                remaining -= len(data)
            yield data


def play(request, id):
    video = VideoInfo.objects.get(id=id)
    path = video.video_path
    """将视频文件以流媒体的方式响应"""
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)
    range_match = range_re.match(range_header)
    size = os.path.getsize(path)
    # content_type, encoding = mimetypes.guess_type(path)
    content_type = 'application/octet-stream'
    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = first_byte + 1024 * 1024 * 1  # 8M 每片,响应体最大体积
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        resp = StreamingHttpResponse(file_iterator(path, offset=first_byte, length=length), status=206,
                                     content_type=content_type)
        resp['Content-Length'] = str(length)
        resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
    else:
        # 不是以视频流方式的获取时，以生成器方式返回整个文件，节省内存
        resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type='application/octet-stream')
        resp['Content-Length'] = str(size)
    resp['Accept-Ranges'] = 'bytes'
    return resp


def upload(request):
    if request.method == 'GET':
        return render(request, 'upload.html')
    files = request.FILES['file']
    file_name = files.name
    if not os.path.exists(os.path.join(BASE_DIR, 'uploads')):
        os.mkdir(os.path.join(BASE_DIR, 'uploads'))
    path = os.path.join(BASE_DIR, 'uploads', file_name)
    f = open(path, 'wb+')
    for file in files.chunks():
        f.write(file)
    f.close()
    add_path(path)
    generate_cover.delay(path)
    return render(request, 'alert.html', {'alert': '视频已添加，稍后就能展示'})


def delete_videos(request):
    shutil.rmtree(os.path.join(BASE_DIR, 'images'))
    shutil.rmtree(os.path.join(BASE_DIR, 'uploads'))
    VideoInfo.objects.all().delete()
    return render(request, 'alert.html', {'alert': '视频库已删除(包括已上传的视频)，请重新添加'})
