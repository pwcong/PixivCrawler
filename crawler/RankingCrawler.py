#!/usr/bin/env python3
# -*- coding: utf8 -*-

import urllib.request
import urllib.parse
import os.path
import utils
import time
import json
import getpass
from bs4 import BeautifulSoup
from api import PixivLoginer
from crawler import PixivItem

pixiv_url_ranking = 'http://www.pixiv.net/ranking.php'
query_mode = (
    'daily',
    'weekly',
    'monthly',
    'rookie',
    'original',
    'male',
    'female'
)
query_format = 'json'


def analysis_html(html):
    items = []
    rootSoup = BeautifulSoup(html, 'lxml')
    selector = rootSoup.select('#wrapper > div.layout-body > div > '
                               'div.ranking-items-container > div.ranking-items.adjust > section')

    for child in selector:
        linkUrl = child.select('div.ranking-image-item > a')[0]['href']
        illust_id = child['data-id']
        thumbnailUrl = child.select('div.ranking-image-item > a > div > img')[0]['data-src']

        author = child['data-user-name']
        browse = child['data-view-count']
        score = child['data-total-score']
        date = child['data-date']
        title = child['data-title']

        originalUrl1 = thumbnailUrl.replace('c/240x480/img-master', 'img-original')
        originalUrl2 = thumbnailUrl.replace('c/240x480/img-master', 'c/1200x1200/img-master')

        items.append(PixivItem(title, illust_id, author, date, browse, score, linkUrl,
                               thumbnailUrl, originalUrl1, originalUrl2))

    return items


def analysis_json(js):

    items = []

    contents = json.loads(js)['contents']

    for child in contents:
        linkUrl = child['url']
        illust_id = child['illust_id']
        thumbnailUrl = child['url']

        author = child['user_name']
        browse = child['view_count']
        score = child['total_score']
        date = child['date']
        title = child['title']

        originalUrl1 = thumbnailUrl.replace('c/240x480/img-master', 'img-original')
        originalUrl2 = thumbnailUrl.replace('c/240x480/img-master', 'c/1200x1200/img-master')

        items.append(PixivItem(title, illust_id, author, date, browse, score, linkUrl,
                               thumbnailUrl, originalUrl1, originalUrl2))

    return items


def get_tt(html):
    rootSoup = BeautifulSoup(html, 'lxml')
    tt = rootSoup.select('#wrapper > footer > div > ul > li')[0].select('form > input')[1]['value']
    return tt


def download_illustration(op, items, picDir):

    print("正在下载中……")

    for item in items:
        try:
            with op.open(item.originalUrl1) as op_img1:
                if op_img1.status == 200:
                    with open(os.path.join(picDir, item.originalUrl1.split('/')[-1]), 'wb') as o:
                        o.write(op_img1.read())
                        print('插图已成功下载 -> %s' % item.get_info())
        except Exception as e:
            try:
                with op.open(item.originalUrl2) as op_img2:
                    if op_img2.status == 200:
                        with open(os.path.join(picDir, item.originalUrl2.split('/')[-1]), 'wb') as o:
                            o.write(op_img2.read())
                            print('插图已成功下载 -> %s' % item.get_info())
            except Exception as e:
                pass

        # 等待1秒，爬得太快容易被发现(￣▽￣)"
        time.sleep(1)

    print("下载完成！")


def download_first(op, mode, picDir):
    visit = pixiv_url_ranking + '?' + urllib.parse.urlencode({'mode': mode})

    tt = None
    items = None

    with op.open(visit) as f:
        if f.status == 200:
            html = utils.ungzip(f.read()).decode()
            tt = get_tt(html)
            items = analysis_html(html)

    if items:
        download_illustration(op, items, picDir)

    return tt


def download_more(op, mode, p, fm, tt, picDir):
    visit = pixiv_url_ranking + '?' + urllib.parse.urlencode({
        'mode': mode,
        'p': p,
        'format': fm,
        'tt': tt
    })

    items = None

    with op.open(visit) as f:
        if f.status == 200:
            js = utils.ungzip(f.read()).decode()
            items = analysis_json(js)

    if items:
        download_illustration(op, items, picDir)


if __name__ == '__main__':

    userid = input("请输入用户名：")
    password = getpass.getpass(prompt="请输入密码：")
    saveDir = input("请输入插图保存文件夹路径：")

    if not os.path.exists(saveDir):
        os.mkdir(saveDir)

    qmNo = input("请选择爬取插图排行榜类型（0：今日 | 1：本周 | 2：本月 | 3：新人 | 4：原创 | 5：受男性欢迎 | 6：受女性欢迎）：")

    if int(qmNo) < 0 or int(qmNo) >6:
        raise Exception("排行榜类型值超出范围")

    opener = PixivLoginer.login(userid, password)

    # 下载第一页插图，并获取重要参数tt
    query_tt = download_first(opener, query_mode[int(qmNo)], saveDir)

    p = 1

    while input("当前第%d页插图已下载完成，是否继续下载第%d页插图？（1：是 | 其他：退出）：" % (p, p + 1)) == '1':
        p += 1
        download_more(opener, query_mode[int(qmNo)], p, query_format, query_tt, saveDir)
