# VPS_Code

## [Debian乱码处理][Debian乱码处理]

## 开机自启
[rc.local][rc.local](/etc/rc.local): 
	
	debian9 开机自启动脚本,用以自启动MO_server.sh文件(放于/etc/目录下，并chmod +x /etc/rc.local给予权限)

[MO_server.sh][MO_server.sh](/root/MO_server.sh): 

	启动自用脚本

## 自启脚本
* **必应每日壁纸获取**

	[GetBingWallpaper.py][GetBingWallpaper.py](/root/GetBingWallpaper.py):
		
		按一定时间(1h)检测[Bing][Bing]主页壁纸是否更新，并将壁纸原图(UHD)下载至“/root/Bing_Wallpaper”,
		并通过Rclone上传到谷歌云盘进行存储

## 电影上传
[MovieShare.sh][MovieShare.sh](/root/MovieShare.sh): 
	
	运行MovieShare.py文件(于Aria2 config中末尾加入"on-download-complete=/root/MovieShare.sh")

[MovieShare.py][MovieShare.py](/root/MovieShare.py): 

	获取电影字幕代码；将电影及其相关文件上传至谷歌云盘（MO_share:/Share）



[Debian乱码处理]:https://blog.csdn.net/qq_32863631/article/details/75314999

[rc.local]:https://raw.githubusercontent.com/mo1055/VPS_Code/master/rc.local
[MO_server.sh]:https://raw.githubusercontent.com/mo1055/VPS_Code/master/MO_server.sh

[GetBingWallpaper.py]:https://raw.githubusercontent.com/mo1055/VPS_Code/master/GetBingWallpaper.py
[Bing]:https://cn.bing.com/

[MovieShare.sh]:https://raw.githubusercontent.com/mo1055/VPS_Code/master/MovieShare.sh
[MovieShare.py]:https://raw.githubusercontent.com/mo1055/VPS_Code/master/MovieShare.py
