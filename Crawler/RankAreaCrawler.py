# !/usr/bin/env python3
# -*- coding: utf8 -*-

import PixivLoginer
from bs4 import BeautifulSoup
from enum import Enum
import time
import os


pixiv_ranking_area_url = 'http://www.pixiv.net/ranking_area.php'
query_type = 'detail'


class AreaNo(Enum):
    beihaidao = 0
    guandong = 1
    zhongbu = 2
    jinji = 3
    zhongguo = 4
    jiuzhou = 5
    guoji = 6


class RankAreaItem(object):
    def __init__(self, illust_id, author, date, browse, score, linkUrl, thumbnailUrl, originalUrl1, originalUrl2):
        self.illust_id = illust_id
        self.author = author
        self.date = date
        self.browse = browse
        self.score = score
        self.linkUrl = linkUrl
        self.thumbnailUrl = thumbnailUrl
        self.originalUrl1 = originalUrl1
        self.originalUrl2 = originalUrl2


def analysis(html):
    items = []
    rootSoup = BeautifulSoup(html, 'lxml')
    selector = rootSoup.select('#wrapper > div.layout-body > div > section > div')
    for child in selector:
        linkUrl = child.select('div.work_wrapper > a')[0]['href']
        illust_id = linkUrl.split('=')[-1]
        thumbnailUrl = child.select('div.work_wrapper > a > div > img')[0]['data-src']

        author = child.select('div.data > a > span')[0].string
        browse = child.select('div.data > dl.slash-separated > dd')[0].string
        score = child.select('div.data > dl.slash-separated > dd')[1].string
        date = child.select('div.data > dl')[1].dd.string

        originalUrl1 = thumbnailUrl.replace('c/150x150/img-master', 'img-original')
        originalUrl2 = thumbnailUrl.replace('c/150x150/img-master', 'c/1200x1200/img-master')

        items.append(RankAreaItem(illust_id, author, date, browse, score, linkUrl,
                                  thumbnailUrl, originalUrl1, originalUrl2))

    return items


def download_illustration(op, no, picDir):

    print("正在下载中……")

    visit = pixiv_ranking_area_url + '?type=' + query_type + '&no=' + str(no)

    op_visit = op.open(visit)
    html = PixivLoginer.ungzip(op_visit.read()).decode()
    op_visit.close()

    items = analysis(html)

    for item in items:

        try:
            op_img1 = op.open(item.originalUrl1)
            if op_img1.status == 200:
                with open(os.path.join(picDir, item.originalUrl1.split('/')[-1]), 'wb') as o:
                    o.write(op_img1.read())
            op_img1.close()
        except:
            try:
                op_img2 = op.open(item.originalUrl2)
                if op_img2.status == 200:
                    with open(os.path.join(picDir, item.originalUrl2.split('/')[-1]), 'wb') as o:
                        o.write(op_img2.read())
                op_img2.close()
            except:
                pass

        time.sleep(1)

    print("下载完成！")


if __name__ == '__main__':

    userid = input("请输入用户名：")
    password = input("请输入密码：")
    saveDir = input("请输入插图保存文件夹路径：")

    areaNo = input("请选择爬取插图排行榜类型（0：北海道 | 1：关东 | 2：中部 | 3：近畿 | 4：中国/四国 | 5：九州/冲绳 | 6：国际）：")

    if int(areaNo) < 0 or int(areaNo) > 6:
        raise Exception("排行榜类型值超出范围")

    opener = PixivLoginer.login(userid, password)

    download_illustration(opener, areaNo, saveDir)
