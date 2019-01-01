/*
这篇爬取的是一个叫“笔趣看”的盗版小说网站
首先从首页爬取所有小说的链接
然后进入详情页爬取每个章节的标题和链接
最后将其存进MongoDB中。
*/

import re
import random
import requests
import pymongo
from time import sleep
from bs4 import BeautifulSoup
from unsplashSpider import useragent

client = pymongo.MongoClient()
test_Database = client.test
headersOfANovel = {
    "Host": "www.biqukan.com",
    "User-Agent": random.choice(useragent.ua),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.biqukan.com/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "If-None-Match": "1546260799",
    "Cache-Control": "max-age=0"
}

headersOfNovels = {
    "Host":"www.biqukan.com",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language":"zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding":"gzip, deflate, br",
    "Referer":"https://www.baidu.com/link?url=0-o4FFuz82SwhCIkugLDqexGqCACbUS_XZrAtFKQUlq&wd=&eqid=df5810d800013573000000045c2b2ed5",
    "Connection":"keep-alive",
    "Upgrade-Insecure-Requests":"1",
    "Cache-Control":"max-age=0"
}

def get_a_novel(url, name):
    html = requests.get(url=url, headers=headersOfANovel)
    Soup = BeautifulSoup(html.text, "lxml")
    dds = Soup.find("div", attrs={"class":"listmain"}).find_all("dd")
    for dd in dds:
        topic = dd.get_text()
        href = dd.a.get("href")
        test_Database[name].insert_one({topic:href})
        # 用小说的名字作为创建集合
        

def get_all_novel(Url):
    html = requests.get(url=Url, headers=headersOfNovels)
    Soup = BeautifulSoup(html.text, "lxml")
    As = Soup.find_all("a", href=re.compile("/\d{1,5}_\d{1,5}/?"))
    page = 0
    for A in As:
        sleep(2)
        page += 1
        print("{}\n".format(page))
        if re.match(".*?\.html", A.get("href")) or A.find("img", alt=True):
        # 这里用来filter一些不合适或者重复的a标签
            continue
        elif re.match("/\d{1,5}_\d{1,5}/?", A.get("href")):
            # 有些href没有网址，要给它加上
            href = "https://www.biqukan.com" + A.get("href")
        else:
            href = A.get("href")
        try:
            get_a_novel(href, A.get_text())
        except Exception as e:
            print(e)
            continue

if __name__ == "__main__":
    get_all_novel("https://www.biqukan.com/")
