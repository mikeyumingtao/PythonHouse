import re
import pymongo
import requests
from time import sleep
from bs4 import BeautifulSoup


class github_crawl():
    num = 0
    followert = 0
    def __init__(self):
        # 初始化一些必要的参数
        self.login_headers = {
            "Referer":"https://github.com/",
            "Host":"github.com",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
        }

        self.logined_headers = {
            "Referer":"https://github.com/login",
            "Host":"github.com",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
        }

        self.login_url = "https://github.com/login"
        self.post_url = "https://github.com/session"
        self.logined_url = "https://github.com/dashboard-feed"
        self.session = requests.Session()
        self.client = pymongo.MongoClient()
        self.textDataBase = self.client.test

    def parse_loginPage(self):
        # 对登陆页面进行爬取，获取token值
        html = self.session.get(url=self.login_url, headers=self.login_headers, verify=False)
        Soup = BeautifulSoup(html.text, "lxml")
        token = Soup.find("input", attrs={"name":"authenticity_token"}).get("value")

        return token
        # 获得了登陆的一个参数

    def login(self, user_name, password):
        # 传进必要的参数，然后登陆
        post_data = {
            "commit":"Sign in",
            "utf8":"✓",
            "authenticity_token":self.parse_loginPage(),
            "login":user_name,
            "password":password
        }

        logined_html = self.session.post(url=self.post_url, data=post_data, headers=self.logined_headers, verify=False)
        if logined_html.status_code == 200:
            dashboardHtml = self.session.get(url=self.logined_url, headers=self.login_headers, verify=False)
            self.parse_loginedHtml(dashboardHtml)

    def parse_loginedHtml(self, Resp):
        # 解析登陆以后的第一个页面，并且获得关注人的最新动态
        Soup = BeautifulSoup(Resp.text, "lxml")
        try:
            raw_users = Soup.find_all("a", attrs={"data-hovercard-type":"user"})
            users_list = []
            for user in raw_users:
                href = "https://github.com" + user.get("href")
                users_list.append(href)
            usersList = list(set(users_list))
            for userhref in usersList:
                self.parse_mainPage(userhref)
                followerUrl = userhref + "?tab=followers"
                self.followerAndfollowing(followerUrl)
                followingUrl = userhref + "?tab=following"
                self.followerAndfollowing(followingUrl)
        except Exception as e:
            print(e)

    def parse_mainPage(self, href):
        mainPage = self.session.get(url=href, headers=self.login_headers, verify=False)
        if mainPage.status_code == 200:
            Soup = BeautifulSoup(mainPage.text, "lxml")
            blogger = Soup.find("title").get_text()
            programs = []
            try:
                lis = Soup.find("ol", attrs={"class":re.compile("pinned-repos-list mb-4.*?")}).find_all("li")
                for li in lis:
                    Popular_Blog = [text for text in li.stripped_strings]
                    programs.append(Popular_Blog)
                    self.textDataBase["someMassages"].insert_one({blogger:programs})
            except Exception as e:
                print(e)
            self.num += 1
            print("爬取了第{}个人的".format(self.num))
            sleep(0.7)

    def followerAndfollowing(self, href):
        """
            由于对关注的人和被关注的人的html爬取都可以使用同一套爬取策略
            所以可以使用同一段代码。
        """
        followingsPage = self.session.get(url=href, headers=self.login_headers, verify=False)
        Soup = BeautifulSoup(followingsPage.text, "lxml")
        try:
            followings = Soup.find_all("span", attrs={"class": "link-gray pl-1"})
            self.followert += len(followings)
            print(self.followert)
            for follower in followings:
                followername = follower.get_text()
                itsHref = "https://www.github.com/" + followername
                print(itsHref)
                self.parse_mainPage(itsHref)
        except Exception as e:
            print(e)




if __name__ == "__main__":
    x = github_crawl()
    x.login("mikeyumingtao", "killer960416")
    print(x.num)
