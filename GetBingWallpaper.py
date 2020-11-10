# import re
import os
import time
import requests
from bs4 import BeautifulSoup

# Bing_Url = "https://cn.bing.com"
Bing_Url = "https://www.bing.com/?mkt=zh-CN&FORM=BEHPTB"
BingWallpaperDir_Path = "/root/Bing_Wallpaper"
BingWallpaper_OldUrl = ""


def BingWallpaper_Save(Image_Url, Image_Note):
    print("开始图片保存")
    print("图片URL：" + Image_Url)
    Image_Path = str(BingWallpaperDir_Path) + '/' + time.strftime("%Y_%m_%d") + Image_Url.split("UHD")[
        -1]
    ImgNote_path = str(BingWallpaperDir_Path) + '/' + time.strftime("%Y_%m_%d") + ".txt"
    print("图片保存目录：" + Image_Path)
    WallpaperRequests = requests.get(Image_Url)
    # print(WallpaperRequests.status_code)
    # 保存图片
    if WallpaperRequests.status_code == 200:
        try:
            with open(Image_Path, 'wb') as f:
                f.write(WallpaperRequests.content)
                f.close()
                print("图片保存成功")
        except IOError:
            print("Error: 没有找到文件或读取文件失败")
    # 保存图片备注
    print("保存图片备注")
    try:
        with open(ImgNote_path, 'w', encoding='utf-8') as f:
            f.write(Image_Note)
            f.write("\nURL: " + Image_Url)
            f.close()
            print("图片备注保存成功")
    except IOError:
        print("Error: 没有找到文件或读取文件失败")
    # 上传图片文件夹
    try:
        os.popen('nohup rclone -v move /root/Bing_Wallpaper/ MO_share:/Share/Picture/Bing_Wallpaper > '
                 '/root/GBShare.out 2>&1 &')
        print("文件上传云盘开始")
    except:
        print("文件上传云盘失败")


def run():
    global BingWallpaper_OldUrl
    try:
        BingRequests = requests.get(Bing_Url)

        if BingRequests.status_code == 200:
            #     获取Text使用re表达式获取壁纸URL

            # BingTarget = re.findall(r'href="(.*?)"', BingRequests.text[:500])[0].split("&")[0].replace("1920x1080",
            # "UHD") BingWallpaper_Url = Bing_Url + BingTarget print(BingWallpaper_Url)

            #     使用bs4库获取壁纸URL与壁纸简介
            BingSoup = BeautifulSoup(BingRequests.text, 'html.parser')
            BingTarget = BingSoup.head.link.get("href").split("&")[0].replace("1920x1080", "UHD")
            BingWallpaper_Url = str(str(Bing_Url) + str(BingTarget))
            BingWallpaper_Name = BingSoup.find_all(id="sh_cp")[0].get("title")
            print(BingWallpaper_Url)
            print(BingWallpaper_Name)
            # 当前壁纸并未保存
            # 保存Bing壁纸图片,图片备注
            if BingWallpaper_OldUrl == BingWallpaper_Url:
                print("该图片已保存")
            else:
                BingWallpaper_Save(BingWallpaper_Url, BingWallpaper_Name)
                BingWallpaper_OldUrl = BingWallpaper_Url
        else:
            print("网络连接失败，状态码: " + str(BingRequests.status_code))
    except:
        print("Bing网页打开失败")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    while True:
        run()
        print("保存时间：" + time.strftime("%a %Y-%m-%d %H:%M:%S", time.localtime()))
        time.sleep(3600)
