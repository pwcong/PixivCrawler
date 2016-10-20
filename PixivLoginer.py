# !/usr/bin/env python3
# -*- coding: utf8 -*-

import urllib.request
import http.cookiejar
import urllib.parse
import re
import gzip
import os.path

pixiv_url_login = "https://accounts.pixiv.net/login"
pixiv_url_login_post = 'https://accounts.pixiv.net/api/login'

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
    'Connection': 'keep-alive',
    'Host': 'accounts.pixiv.net',
    'Referer': 'http://www.pixiv.net/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/50.0.2661.102 Safari/537.36'
}


def getopener(header):
    cj = http.cookiejar.CookieJar()
    cp = urllib.request.HTTPCookieProcessor(cj)
    op = urllib.request.build_opener(cp)
    h = []
    for key, value in header.items():
        elem = (key, value)
        h.append(elem)
    op.addheaders = h
    return op


def getpostkey(body):
    res = re.search('name="post_key" value="\w*', body)
    if res:
        return res.group().split('"')[-1]
    else:
        return None


def ungzip(data):
    try:
        data = gzip.decompress(data)
    except Exception as e:
        print(e)
    return data


def login(uid, pwd):
    op = getopener(headers)

    # 访问登陆界面，获取登陆所需的post_key
    op_key = op.open(pixiv_url_login)

    data = op_key.read()
    op_key.close()
    data = ungzip(data).decode()

    # 初始化登陆所需提交的数据
    pixiv_key = getpostkey(data)
    pixiv_id = uid
    pixiv_password = pwd
    pixiv_source = 'accounts'

    post_data = {
        'pixiv_id': pixiv_id,
        'password': pixiv_password,
        'post_key': pixiv_key,
        'source': pixiv_source
    }
    post_data = urllib.parse.urlencode(post_data).encode('utf-8')

    # 提交登录数据
    op_login = op.open(pixiv_url_login_post, post_data)
    op_login.close()

    # 返回带cookie管理的opener
    return op


if __name__ == '__main__':

    pixiv_url_login_test = 'http://i4.pixiv.net/img-original/img/2016/10/12/19/26/44/59432931_p0.jpg'

    userid = input("请输入用户名：")
    password = input("请输入密码：")
    path = input("请输入测试图片保存文件夹路径：")

    # 登陆Pixiv
    opener = login(userid, password)

    # 下载Pixiv大图测试是否登录成功
    with opener.open(pixiv_url_login_test) as i:
        if i.status == 200:
            print("登陆成功！")
            print("开始下载测试图片！")

            with open(os.path.join(path, pixiv_url_login_test.split('/')[-1]), 'wb') as o:
                o.write(i.read())
            print("下载完成！")
