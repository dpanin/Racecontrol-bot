""" This module checks for new posts and then gets the main text and image."""
from contextlib import contextmanager
import urllib.response
import urllib.request
import datetime
import hashlib
import shutil
import signal
import time
import feedparser
import tokens.py
import telebot
from bs4 import BeautifulSoup
from retrying import retry


FEED_URL = ("http://racecontrol.me/site/rss")
NET_TIMEOUT = 10*1000
CHANNEL_NAME = ''

bot = telebot.TeleBot(BOT_TOKEN)

# FUNCS


class TimeoutException(Exception):

    """Timeout"""
    pass


@contextmanager
def timeout_sec(seconds):
    """Send error message if timeout"""
    def signal_handler(signum, frame):
        raise TimeoutException(Exception("Timed out!"))
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


@retry(wait_fixed=NET_TIMEOUT)
def image_download(i):
    """Download images from RSS feed"""
    desc = i.description
    soup_desc = BeautifulSoup(desc, "lxml")
    # Download file and save under hash of the post link if image exists
    link_hash = hashlib.md5(i.link.encode('utf-8')).hexdigest()
    filename = ""
    filename = filename.join(["tmp/", link_hash, ".jpeg"])
    try:
        with urllib.request.urlopen(soup_desc.img['src']) as response, \
                open(filename, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
    except TypeError:
        print("Image not found")


@retry(wait_fixed=NET_TIMEOUT)
def get_feed():
    """Get RSS feed"""
    f = feedparser.parse(FEED_URL)
    return f


@retry(wait_fixed=NET_TIMEOUT)
def get_post(i):
    """Get main text from URL"""
    post_page = urllib.request.urlopen(i)
    html = post_page.read()
    soup = BeautifulSoup(html, "lxml")
    post = soup.find("div", class_="post-news-lead")
    post = post.text
    post = post.replace(u'\xa0', u' ')
    return post


def main():
    print('Begin processing the feed...')
    # Defining variables
    LINKS = []
    IMAGES = []
    i = 0

    f = get_feed()
    FILE = open('time.txt', 'r')
    LAST_DATE = float(FILE.read())
    FILE.close()

    # Finding newer posts by comparing time
    for i in f['entries']:
        converted_time = time.mktime(datetime.datetime.strptime(
            i.published, "%a, %d %b %Y %X %z").timetuple())
        if converted_time > LAST_DATE:
            LINKS.append(i.link)
            image_download(i)
        else:
            break

    # Get text from news and send it and photo to telegram channel
    for i in reversed(LINKS):
        post = get_post(i)
        bot.send_message(CHANNEL_NAME, post)
        try:
            # Trying to find photo for the post
            photo = open("{0}{1}{2}".format(
                "tmp/", hashlib.md5(i.encode('utf-8')).hexdigest(), ".jpeg"), 'rb')
            bot.send_photo(CHANNEL_NAME, photo)
        except FileNotFoundError:
            continue
        # For debugging
        print(post)

    # Write latest post time to file
    FILE = open('time.txt', 'w')
    FILE.write(str(time.mktime(datetime.datetime.strptime(
        f.entries[0].published, "%a, %d %b %Y %X %z").timetuple())))
    FILE.close()

while True:
    main()
    print("Going to sleep for 30 seconds")
    time.sleep(30)
