import imageio
from PIL import Image
import time
import os
from django.conf import settings


# 直接调用函数时使用
# from video import settings


# 生成视频封面
def generate_cover(path):
    dir_path, file = os.path.split(path)
    # 有些视频文件名中可能会有‘.’ 将文件名按从右往左的方向按‘.’分割一次，分成两部分
    file_name, file_ext = file.rsplit('.', 1)

    start = time.time()
    reader = imageio.get_reader(path)
    # 获取视频的总帧数
    size = reader.count_frames()
    # 选取中间的一帧作为视频封面
    middle = size // 2
    middle_frame = reader.get_data(middle)
    img = Image.fromarray(middle_frame)
    # 重新设置图片大小
    final_img = img.resize((180, 180))

    if not os.path.exists(os.path.join(settings.BASE_DIR, 'images')):
        os.mkdir(os.path.join(settings.BASE_DIR, 'images'))
    final_img.save(os.path.join(os.path.join(settings.BASE_DIR, 'images'), file_name) + '.jpg')
    print(time.time() - start)
    reader.close()
