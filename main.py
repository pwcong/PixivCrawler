#!/usr/bin/env python3
# -*- coding: utf8 -*-

import getpass
import os
from api import PixivLoginer
from crawler import RankingCrawler


if __name__ == '__main__':
    userid = input("请输入用户名：")
    password = getpass.getpass(prompt="请输入密码：")
    saveDir = input("请输入插图保存文件夹路径：")

    if not os.path.exists(saveDir):
        os.mkdir(saveDir)

    qmNo = input("请选择爬取插图排行榜类型（0：今日 | 1：本周 | 2：本月 | 3：新人 | 4：原创 | 5：受男性欢迎 | 6：受女性欢迎）：")

    if int(qmNo) < 0 or int(qmNo) > 6:
        raise Exception("排行榜类型值超出范围")

    opener = PixivLoginer.login(userid, password)

    query_tt = RankingCrawler.download_first(opener, RankingCrawler.query_mode[int(qmNo)], saveDir)

    p = 1

    while input("当前第%d页插图已下载完成，是否继续下载第%d页插图？（1：是 | 其他：退出）：" % (p, p + 1)) == '1':
        p += 1
        RankingCrawler.download_more(opener, RankingCrawler.query_mode[int(qmNo)], p,
                                     RankingCrawler.query_format, query_tt, saveDir)