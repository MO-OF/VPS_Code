# 文件上传监控
import os
import re
import requests
import time
import shutil

# FileShare.out日志文件目录
fileShare_out_path = "/root/FileShare.out"
fileShare_err_dir = "/root/Download"
# Server_Socket设置
server_SCKEY = "SCU155246T3dd6084bb58c470f8b9c045c904e25ef600feb7283347"
# requests代理设置
proxies = {"http": None, "https": None}


# 通过Server酱发送信息到Wechat，post方法
# title：标题
# content：内容，支持MarkDowm语法
def wechatSend(title, content):
    data = {"text": title, "desp": content}
    wechatSend_url = "https://sc.ftqq.com/{server_SCKEY}.send".format(server_SCKEY=server_SCKEY)
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


def run():
    fileShare_mem_size = 0
    while True:
        # 检测上传程序是否仍在运行(FileShare.out是否在70s内有所增加)
        # 上传文件总数不对且上传程序检测无运行即返回失败并截取部分输出信息一并返回
        file_ExistsOrCreat(fileShare_out_path)
        fileShare_size = os.path.getsize(fileShare_out_path)
        # fileShare.out文件有输出且70s内无变化，进行信息确认
        if fileShare_size == fileShare_mem_size != 0:
            # print("有信息")
            f = open(fileShare_out_path, "r")
            fileShare_out_text = f.read()
            f.close()
            out_lists = re.findall(r".*?INFO.{5,}Copied", fileShare_out_text)
            if out_lists:
                title = "文件上传成功"
                content = "已上传文件清单："
                for out_list in out_lists:
                    content = content + "\n\n" + out_list
            else:
                fileShare_err_path = fileShare_err_dir + "/" + str(
                    time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())) + "_fileShare_err.txt"
                # 文件a移动到b，全路径
                shutil.move(fileShare_out_path, fileShare_err_path)
                title = "文件上传失败"
                content = "请打开FileShare.out进行查看\n\n文件路径：" + fileShare_err_path
            wechatSend(title, content)
            clear_File(fileShare_out_path)
        fileShare_mem_size = fileShare_size
        # print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\tNo file share completed", end="\r")
        time.sleep(70)


if __name__ == '__main__':
    run()
