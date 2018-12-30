import requests
import os
from unsplashSpider import useragent
import random
from time import sleep

headers = {
    "User-Agent":"{}".format(random.choice(useragent.ua))
}

def get_one_pic(url, header, page, order):
    headers = {
        "User-Agent": "{}".format(header),
        "Host": "images.unsplash.com"
    }
    html = requests.get(url=url, headers=headers)
    with open("{}\{}.jpg".format(page, order), "wb") as f:
        f.write(html.content)

def get_urls(page_url, header, page):
    headers = {
        "User-Agent": "{}".format(header),
        "Referer": "https://unsplash.com/",
        "Host": "unsplash.com"
    }
    x = 0
    html = requests.get(url=page_url, headers = headers)
    sleep(0.1)
    os.mkdir("{}".format(page))
    for per in html.json():
        x += 1
        url = per.get("urls").get("raw")+"&auto=format&fit=crop&w=600&q=60"
        get_one_pic(url, header, page, x)

def main():
    for page in range(9, 18):
        header = random.choice(useragent.ua)
        page_url = "https://unsplash.com/napi/photos?page={}&per_page=12".format(page)
        sleep(2)
        get_urls(page_url, header, page)

if __name__ == "__main__":
    main()

