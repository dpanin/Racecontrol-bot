""" This module checks for new posts and then gets the main text and image."""
import urllib.request
import datetime
import hashlib
import shutil
import time
import os
import re
import feedparser
import telegram
from bs4 import BeautifulSoup
from retrying import retry

BOT_TOKEN = os.environ.get('TOKEN')
FEED_URL = 'http://racecontrol.me/site/rss'
NET_TIMEOUT = 10*1000
CHANNEL_NAME = '@RacecontrolNews'
TIME = os.environ.get('TIME')
bot = telegram.Bot(BOT_TOKEN)


# FUNCS

@retry(wait_fixed=NET_TIMEOUT)
def parse_post(i):
    post_page = urllib.request.urlopen(i.link)
    html = post_page.read()
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find(
        "div", class_="post-news-lead").text.replace(u'\xa0', u' ')
    title = soup.find(
        "h3", class_="post-news-title").text.replace(u'\xa0', u' ')
    body = re.sub(' +', ' ', body)
    post = "<b>" + title + "</b>" + "\n\n" + body + " " + i.link
    return post


@retry(wait_fixed=NET_TIMEOUT)
def send_post(i):
    """Send main text  and title from RSS"""
    post = parse_post(i)
    bot.send_message(
        chat_id=CHANNEL_NAME, text=post, parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=True)
    time.sleep(1)


@retry(wait_fixed=NET_TIMEOUT)
def send_image(i):
    """Send images from RSS feed"""
    desc = i.description
    soup_desc = BeautifulSoup(desc, "html.parser")
    # Download file and save under hash of the post link if image exists
    link_hash = hashlib.md5(i.link.encode('utf-8')).hexdigest()
    filepath = ""
    filepath = filepath.join(["tmp/", link_hash, ".jpeg"])
    with urllib.request.urlopen(soup_desc.img['src']) as response, \
            open(filepath, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    bot.send_photo(chat_id=CHANNEL_NAME, photo=open(filepath, 'rb'))
    os.remove(filepath)
    time.sleep(1)


def save_time(time_string):
    # Write latest post time to file
    file = open('time.txt', 'w')
    file.write(str(time.mktime(datetime.datetime.strptime(
        time_string, "%a, %d %b %Y %X %z").timetuple())))
    file.close()


def main():
    '''Main function'''
    f = feedparser.parse(FEED_URL)
    with open('time.txt') as file:
        last_date = float(file.read())
    # Finding newer posts by comparing time
    for i in reversed(f['entries']):
        converted_time = time.mktime(datetime.datetime.strptime(
            i.published, "%a, %d %b %Y %X %z").timetuple())
        if converted_time > last_date:
            send_post(i)
            send_image(i)
            save_time(i.published)

# MAIN
with open('time.txt', 'w') as file:
    if TIME == "-1":
        file.write(str(round(time.time())))
    else:
        file.write(TIME)

while True:
    main()
    time.sleep(30)
