# video
基于django的个人视频网站
启动方式：下载源码，安装所需包，启动django，并在命令行启动celery  如： celery -A video worker -l info。
首次打开网站，输入绝对路径即可自动识别路径下的mp4文件，并选取视频所有帧的中间那帧作为封面（大概就是视频一半时刻的图像），分页展示在首页。
也可以自行上传视频（保存在项目根目录下uploads文件夹），提供搜索功能
注：封面生成仅在linux下使用（即celery使用）

首次打开首页：
![](https://github.com/allenliuchina/video/blob/master/screenshot/1.png)

添加完路径后首页
![](https://github.com/allenliuchina/video/blob/master/screenshot/2.png)

播放页面
![](https://github.com/allenliuchina/video/blob/master/screenshot/4.png)

搜索页面
![](https://github.com/allenliuchina/video/blob/master/screenshot/3.png)
