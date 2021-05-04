# coding=utf-8
# creat_time:2021-05-04
import os
import re
import time
import requests
import hashlib
import json

# 日志文件目录
aria2_log_file = "/root/.aria2/aria2.log"
# requests代理设置
proxies = {"http": None, "https": None}
# 媒体文件对应后缀
movie_type = ["mkv", "mp4", "m4v", "webm", "mov", "avi", "wmv", "mpg", "fly"]
# Server_Socket设置
server_SCKEY = "SCT35953TS0BKCLK6oZVLbOuee3VQS8oz"


# 通过Server酱发送信息到Wechat，post方法
# server_SCKEY 在server酱中获取
# title：标题
# content：内容，支持MarkDowm语法
def wechatSend(title, content):
    data = {"text": title, "desp": content}
    wechatSend_url = "https://sctapi.ftqq.com/{server_SCKEY}.send".format(server_SCKEY=server_SCKEY)
    j = 0
    while j < 10:
        try:
            # 使用post方法进行发送
            r = requests.post(wechatSend_url, data=data, proxies=proxies, timeout=15)
            if r.status_code == 200:
                if re.findall(r"\bsuccess\b", r.text):
                    print("\nWechat message send success: {title}\n".format(title=title))
                else:
                    print("Wechat消息发送失败：\n")
                    print(r.text)
                break
            else:
                j = j + 1
                print("连接状态码：{code}".format(code=r.status_code))
                print("Wechat信息发送失败 {j} 次".format(j=j))
        except Exception as err:
            j = j + 1
            print("Wechat信息发送失败 {j} 次".format(j=j))
            # 这个是输出错误类别的，如果捕捉的是通用错误，其实这个看不出来什么
            print("\nerror: \t{0}\n".format(str(err)))


# 清空file_path中的所有内容，若无该文件将创建
def clear_File(file_path):
    f = open(file_path, "w")
    f.close()


# 判断file_path文件是否存在，不存在则创建
def file_ExistsOrCreat(file_path):
    if not os.path.exists(file_path):
        clear_File(file_path)


# 获取电影文件的名为cid值用于迅雷字幕的下载
# 使用SHA1摘要算法
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


# 字幕文件保存在媒体文件所在目录(target_path),字幕URL(sub_url)
# 保存成功返回1，失败返回0
def save_Subfile(sub_url, target_path, i):
    result = 0
    # 字幕保存路径，媒体文件名称.svote_{svote}.{sun_type}
    sub_path = target_path.replace(target_path.split(".")[-1],
                                   "XL_{i}.{sub_type}".format(i=i, sub_type=sub_url.split(".")[-1]))
    # 网络连接模板
    j = 0
    while j < 10:
        try:
            r = requests.get(sub_url, proxies=proxies, timeout=15)
            if r.status_code == 200:
                print("字幕文件获取成功")
                with open(sub_path, 'wb') as f:
                    f.write(r.content)
                    f.close()
                print(sub_path.split('/')[-1] + "字幕保存成功(save_Subfile)")
                result = 1
                break
            else:
                j = j + 1
                print("连接状态码：{code}".format(code=r.status_code))
                print("字幕文件网页连接失败 {j} 次".format(j=j))
        except Exception as err:
            j = j + 1
            print("字幕文件网页连接失败 {j} 次".format(j=j))
            # 这个是输出错误类别的，如果捕捉的是通用错误，其实这个看不出来什么
            print("\nerror: \t{0}\n".format(str(err)))
    return result


# 获取目标媒体文件(target_path)字幕列表，并遍历进行保存
def get_subtitle(target_path):
    # 记录成功下载的数量
    sub_success = 0
    # 获取目标媒体文件名
    target_name = target_path.split("/")[-1].replace(target_path.split("/")[-1].split(".")[-1], "")[:-1]
    print("文件名：{0}".format(target_name))
    # 获取媒体文件cid值得到迅雷字幕列表URL
    cid_url = "http://sub.xmp.sandai.net:8000/subxl/{cid}.json".format(cid=cid_hash_file(target_path))
    # 尝试打开迅雷字幕列表URL
    j = 0
    while j < 10:
        try:
            r = requests.get(cid_url, proxies=proxies, timeout=15)
            if r.status_code == 200:
                # 将URL内容转换为json文本
                # 最后一个为空去除
                sub_lists = json.loads(r.text)["sublist"][:-1]
                # 判断是否有字幕文件
                if not len(json.loads(r.text)["sublist"][:-1]):
                    # 无字幕文件，发送错误信息
                    title = "媒体文件迅雷无字幕列表"
                    content = "文件名：" + target_name + " 迅雷字幕列表为空"
                    wechatSend(title, content)
                    print(title)
                # 有弹幕判断是否有参考价值
                else:
                    # 首个字幕投票率低于100，证明后续列表均无参考价值(列表为降序排列)，不进行下载
                    if sub_lists[0]["svote"] < 100:
                        title = "媒体文件迅雷字幕参考率低"
                        content = "文件名：{file_name}\n\n字幕投票率：{svote}\n\n字幕URL：{surl}" \
                            .format(file_name=target_name,
                                    svote=sub_lists[0]["svote"],
                                    surl=sub_lists[0]["surl"])
                        wechatSend(title, content)
                        print(title)
                    # 有弹幕且有参考价值，进行下载
                    else:
                        for i in range(len(sub_lists)):
                            # 仅保存投票率高于100的字幕文件
                            if sub_lists[i]["svote"] > 100:
                                print("保存字幕文件{sub_name}".format(sub_name=sub_lists[i]["sname"]))
                                print(i)
                                # 逐个字幕保存
                                if save_Subfile(sub_lists[i]["surl"], target_path, i):
                                    sub_success = sub_success + 1
                        if sub_success > 0:
                            title = "媒体文件迅雷字幕保存成功"
                            content = "文件名：{file_name}\n\n字幕下载成功数：{sub_success}" \
                                .format(file_name=target_name,
                                        sub_success=sub_success)
                            wechatSend(title, content)
                            print(title)
                        else:
                            title = "媒体文件迅雷字幕保存失败"
                            content = "文件名：{file_name}\n\n字幕下载成功数：{sub_success}" \
                                .format(file_name=target_name,
                                        sub_success=sub_success)
                            wechatSend(title, content)
                            print(title)
                break
            else:
                j = j + 1
                print("打开字幕列表网页失败 {j} 次".format(j=j))
        except Exception as err:
            j = j + 1
            print("打开字幕列表网页失败 {j} 次".format(j=j))
            print("\nerror: \t{0}\n".format(str(err)))
    if j == 10:
        title = "打开字幕列表网页失败 {j} 次".format(j=j)
        content = "文件名：{file_name}\n\n字幕列表URL：{cid_url}" \
            .format(file_name=target_name,
                    cid_url=cid_url)
        wechatSend(title, content)
        print(title)


# 文件遍历，返回列表形式每个文件的全路径
def file_Traverse(target_path):
    file_list = []
    for dirpath,dirname,filenames in os.walk(target_path):
        for filename in filenames:
            file_list.append(dirpath + "/" + filename)
    return file_list


# 分享程序
# 通过rclone分享file_path路径中的所有文件
def DriverShare(file_path):
    print("Sharing Start")
    print("上传文件路径：" + file_path)
    try:
        # >> 为追加输出，>为覆盖输出
        os.popen(
            "nohup rclone -v move {file_path} MO_share:/Share >> /root/FileShare.out 2>&1 &".format(file_path=file_path))
        # 发送文件开始上传消息到Wechat
        title = "VPS文件开始上传"
        content = "文件名：" + file_path
        wechatSend(title, content)
        print(title)
    except:
        print("文件上传云盘失败")
        # 发送文件上传失败消息到Wechat
        title = "VPS文件上传失败"
        content = "文件名：" + file_path
        wechatSend(title, content)
        print(title)


def run():
    # run()主函数
    # 检测aria2.log日志，每10s一次
    while True:
        # 判断aria2.log文件是否存在，不存在则创建
        file_ExistsOrCreat(aria2_log_file)
        # 只读方式打开aria2.log日志
        f = open(aria2_log_file, "r")
        aria2_log_text = f.read()
        f.close()
        # 使用re来检测aria2.log日志查询是否有文件下载完成
        if re.findall(r"\bDownload complete: \/root\/Download.*", aria2_log_text):
            # 删除.aria2临时文件
            os.popen('rm -rf /root/Download/*.aria2')
            time.sleep(1)
            # 有文件下载完成，获取文件实际路径，仅对下载好的该文件或文件夹操作
            file_path = re.findall(r"\bDownload complete: \/root\/Download.*", aria2_log_text)[-1].replace(
                "Download complete: ", "")
            print(file_path)
            # 获取已完成文件路径，清空aria2.log日志等待下次文件下载完成
            clear_File(aria2_log_file)
            # 发送文件下载成功消息到Wechat
            title = "VPS文件下载成功"
            content = "文件名：" + file_path
            wechatSend(title, content)
            # 开始文件遍历，若为媒体文件则进行字幕获取
            print("\n开始文件遍历\n文件路径：{0}".format(file_path))
            for file_list_path in file_Traverse(file_path):
                # 判断该文件是否为媒体文件，是就进行字幕搜索
                if re.findall(file_list_path.split(".")[-1], str(movie_type)):
                    print("检测到该文件为媒体文件，进行字幕查询")
                    print("文件路径：" + file_list_path)
                    get_subtitle(file_list_path)
            print("\n开始文件上传\n文件路径：{0}".format(file_path))
            DriverShare(file_path)
        # else:
            # 尚未有文件下载完成
            # print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\tNo file download completed", end="\r")
        time.sleep(10)


if __name__ == '__main__':
    run()
