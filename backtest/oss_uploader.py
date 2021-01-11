# coding=utf-8

# @Author : Lucas
# @Date   : 2021/1/9 6:41 pm
# @Last Modified by:  Lucas
# @Last Modified time:
import os
from itertools import islice

import oss2

ACCKEY = 'LTAI4G88CoREvC1v19yhG8tV'
Secret = 'qRbu0JY9WdErqo4pwPWftfUQQ2tq0h'
Bucket = 'vimeracke'


def list_oss():
    auth = oss2.Auth(ACCKEY, Secret)
    # Endpoint以杭州为例，其它Region请按实际情况填写。
    bucket = oss2.Bucket(auth, 'http://oss-cn-shenzhen.aliyuncs.com', Bucket)

    # oss2.ObjectIteratorr用于遍历文件。
    for b in islice(oss2.ObjectIterator(bucket), 10):
        print(b.key)


def upload_pic(file: str):
    # 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
    auth = oss2.Auth(ACCKEY, Secret)
    # Endpoint以杭州为例，其它Region请按实际情况填写。
    bucket = oss2.Bucket(auth, 'http://oss-cn-shenzhen.aliyuncs.com', Bucket)

    # <yourObjectName>上传文件到OSS时需要指定包含文件后缀在内的完整路径，例如abc/efg/123.jpg。
    # <yourLocalFile>由本地文件路径加文件名包括后缀组成，例如/users/local/myfile.txt。
    file = os.path.abspath(file)
    print(file)
    return bucket.put_object_from_file(f'fuck/{file}', file)


if __name__ == '__main__':
    from rich import print

    print("Hello, [bold magenta]World[/bold magenta]!", ":vampire:", locals())
    # list_oss()
