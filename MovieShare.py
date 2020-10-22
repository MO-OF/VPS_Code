#coding=utf-8
import re
import os
import json
import hashlib
import requests
import time

movie_type = ["mkv", "mp4", "m4v", "webm", "mov", "avi", "wmv", "mpg", "fly"]
path = "/root/Download"
del_text = ".torrent"

fail_list = []

# 获取电影文件的名为cid和hash值用于迅雷字幕的下载
def cid_hash_file(path):
    '''
    计算文件名为cid的hash值，算法来源：https://github.com/iambus/xunlei-lixian
    :param path: 需要计算的本地文件路径
    :return: 所给路径对应文件的cid值
    '''
    h = hashlib.sha1()
    size = os.path.getsize(path)
    with open(path, 'rb') as stream:
        if size < 0xF000:
            h.update(stream.read())
        else:
            h.update(stream.read(0x5000))
            stream.seek(size // 3)
            h.update(stream.read(0x5000))
            stream.seek(size - 0x5000)
            h.update(stream.read(0x5000))
    return h.hexdigest().upper()


# 获取迅雷字幕库中字幕信息列表
def get_sub_info_list(cid, file, max_retry_times = 30):
    '''
    获取迅雷字幕库中字幕信息列表
    :param cid: 本地电影文件的cid值
    :param max_retry_times: 最大重试次数，非正数时会无限次重试直到获得正确结果
    :return: 字幕信息列表，超过最大重试次数还未获得正确结果时会返回None。
    '''
    # print(cid)
    url = "http://sub.xmp.sandai.net:8000/subxl/{cid}.json".format(cid=cid)
    result = None
    if max_retry_times <= 0:
        while True:
            response = requests.get(url)
            if response.status_code == 200:
                result = json.loads(response.text)["sublist"]
                break
    else:
        for i in range(max_retry_times):
            response = requests.get(url)
            if response.status_code == 200:
                try:
                    result_dict = json.loads(response.text)
                    result = result_dict["sublist"]
                    print("获取" + file.split('/')[-1] + "迅雷字幕信息列表成功")
                    break
                except:
                    print("获取"+file.split('/')[-1]+"迅雷字幕信息列表失败")
                    break
    # print(i)
    # print(result)  # 字幕列表数目
    if result:
        return [i for i in result if i]
    else:
        return None


# 获取总路径中各电影的实际路径
def get_files(path):
    files = os.listdir(path)  # 获取path目录下的文件和文件夹，数组方式
    for file in files:
        path_file = path+"/"+file
        if os.path.isdir(path_file):
            # 若path_file为文件夹，进行递归操作
            get_files(path_file)
        else:
            for i in movie_type:
                # 属于电影格式的文件
                if re.findall(i, path_file):
                    # print(path_file)  # 输出电影路径
                    print("================================视频字幕获取=================================")
                    get_ass(path_file, path)
                    print("\n\n\n\n")


# 获取字幕
def get_ass(file, path):
    # 获取一个本地电影文件名为cid的hash值
    cid = cid_hash_file(file)
    # print(cid)
    # print(file.split("/")[-1])  # 获取电影全名
    info_list = get_sub_info_list(cid, file)
    # print(info_list)  # 显示字幕列表详细信息
    # print(len(info_list))  # 显示字幕数量
    if info_list:
        print("获取"+file.split('/')[-1]+"迅雷字幕成功")
        # print(file)
        # print(path)
        save_Thunder_subtitles(info_list,path,file)
    else:
        print("获取"+file.split('/')[-1]+"迅雷字幕失败")
        fail_list.append(file.split('/')[-1])
    # else:


# # ass字幕转为srt字幕
# def ass_to_srt(file):
#     print('ass格式开始修改为srt格式')
#     # print(file)
#     ass_file = open(file, 'r')
#     # print(ass_file)
#     try:
#         srt_str = asstosrt.convert(ass_file)
#         srt_str_byte = bytes(srt_str, encoding='UTF-8')
#         # print(srt_str)
#         # print(file.split('ass')[0] + 'srt')
#         new_file_path = file.split('ass')[0] + 'srt'
#         with open(new_file_path, 'wb') as f:
#             f.write(srt_str_byte)
#             f.close()
#         # print(srt_str)
#         print('ass转srt格式已完成：' + new_file_path)
#     except Exception as e:
#         print('字幕转码异常')
#         print('Reason:',e)


# 保存迅雷字幕
def save_Thunder_subtitles(list,path,file):
    # print(list)  # 显示字幕列表详细信息
    print("字幕数量:"+str(len(list)))  # 显示字幕数量
    print("保存"+file.split('/')[-1]+"迅雷字幕")
    num = 0
    sav_on = 0  # 视频字幕保存成功数目
    for i in list:
        num = num + 1
        # print(num)
        # print(i)
        url = str(i).split("'surl': '")[-1].split("'")[0]
        print(url)
        j = 0
        while j < 10:
            try:
                r = requests.get(url, timeout = 15)
                if(r.status_code == 200):
                    subtitle_path = str(path+"/"+file.split("/")[-1])[:-4]+"."+"XL"+str(num)+"."+url.split(".")[-1]
                    # print(file_path)  # 字幕保存全路径
                    with open(subtitle_path, 'wb') as f:
                        f.write(r.content)
                        f.close()
                    print(subtitle_path.split('/')[-1]+"字幕保存成功")
                    # 不更改ass格式了
                    # if url.split(".")[-1] == 'ass':
                    #     # 字幕为ass格式，将其改为srt格式
                    #     ass_to_srt(subtitle_path)
                    #     os.remove(subtitle_path)
                    #     print("原ass字幕文件已删除：" + subtitle_path)
                    # sav_on = sav_on + 1  # 有至少一个字幕文件保存成功
                    break
                    # except:
                    #     print(file.split('/')[-1] + "字幕保存失败")
                else:
                    j = j + 1
                    print(file.split('/')[-1] + "字幕连接失败,共失败 " + str(j) +' 次')
            except Exception as e:
                j = j + 1
                print("获取" + file.split('/')[-1] + "迅雷字幕文件超时 " + str(j) + ' 次')
                print('Reason:', e)
    if sav_on == 0:
        print(file.split('/')[-1] + "所有字幕均保存失败")
        fail_list.append(file.split('/')[-1])


# 获取字幕主程序
def subtitle_main(path):
    print("now get movie subtitle")
    get_files(path)  # 获取总路径中各电影的实际路径
    print("字幕获取失败数目:"+str(len(fail_list)))
    for i in fail_list:
        print(i+"字幕获取失败")


# 分享主程序
def DriverShare():
    print("Sharing Start")
    # os.popen('rm -rf /root/Download/*.aria2')
    # time.sleep(10)
    try:
        os.popen('nohup rclone -v move /root/Download/ MO_share:/Share > /root/GSshare.out 2>&1 &')
        print("文件上传云盘开始")
    except:
        print("文件上传云盘失败")


# def Del_file():
#     # os.popen('rm -rf /root/Download/*')
#     # os.popen('rm -rf /root/nohup.out')
#     print("all is delete")

def main():
    print("谷歌云盘上传程序启动，先行等待30S")
    time.sleep(1)
    os.popen('rm -rf /root/Download/*.aria2')
    file_num = len(os.popen('ls /root/Download/').readlines())
    file_size = os.popen('du -sk /root/Download').readlines()[0].split('/')[0]
    os.popen('rm -rf /root/Download/*'+del_text)
    new_file_num = len(os.popen('ls /root/Download/').readlines())
    new_file_size = os.popen('du -sk /root/Download').readlines()[0].split('/')[0]
    if(file_num != 0):
        if(file_size == new_file_size):
            if(file_num == new_file_num):
                subtitle_main(path)
                DriverShare()
                # Del_file()
            else:
                print("just BT file")
        else:
            print("影片未下载完毕")
    else:
        print("This is an empty folder")
    

if __name__ == "__main__":
        main()
