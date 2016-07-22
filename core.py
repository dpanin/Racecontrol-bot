""" This module checks for new posts and then gets the main text and image."""
import urllib.response
import urllib.request
import datetime
import hashlib
import logging
import shutil
import time
import os
import feedparser
from tokens import BOT_TOKEN
import telebot
from bs4 import BeautifulSoup
from retrying import retry


FEED_URL = ("http://racecontrol.me/site/rss")
NET_TIMEOUT = 10*1000
CHANNEL_NAME = '@RacecontrolNews'

bot = telebot.TeleBot(BOT_TOKEN)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='tmp/app.log',
                    filemode='w')

# FUNCS


@retry(wait_fixed=NET_TIMEOUT)
def image_download(i):
    """Download images from RSS feed"""
    desc = i.description
    soup_desc = BeautifulSoup(desc, "html.parser")
    # Download file and save under hash of the post link if image exists
    link_hash = hashlib.md5(i.link.encode('utf-8')).hexdigest()
    filename = ""
    filename = filename.join(["tmp/", link_hash, ".jpeg"])
    try:
        logging.debug('Downloading photo %s' % i.link)
        with urllib.request.urlopen(soup_desc.img['src']) as response, \
                open(filename, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
    except TypeError:
        logging.warning("Image not found")


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
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find(
        "div", class_="post-news-lead").text.replace(u'\xa0', u' ')
    title = soup.find(
        "h3", class_="post-news-title").text.replace(u'\xa0', u' ')
    post = "*" + title + "*" + "\n\n" + body + " " + i
    return post


def main():
    '''Main function'''
    logging.info('Begin processing the feed')
    # Defining variables
    links = []
    i = 0

    f = get_feed()
    file = open('time.txt', 'r')
    last_date = float(file.read())
    file.close()

    # Finding newer posts by comparing time
    logging.debug("Comparing time")
    for i in f['entries']:
        converted_time = time.mktime(datetime.datetime.strptime(
            i.published, "%a, %d %b %Y %X %z").timetuple())
        if converted_time > last_date:
            links.append(i.link)
            image_download(i)
        else:
            break

    # Get text from news and send it and photo to telegram channel
    for i in reversed(links):
        post = get_post(i)
        bot.send_message(
            CHANNEL_NAME, post, parse_mode="markdown", disable_web_page_preview=True)
        logging.debug("Post %s sent" % i)
        time.sleep(1)
        try:
            # Trying to find photo for the post
            photo_name = "{0}{1}{2}".format(
                "tmp/", hashlib.md5(i.encode('utf-8')).hexdigest(), ".jpeg")
            photo = open(photo_name, 'rb')
            bot.send_photo(CHANNEL_NAME, photo)
            logging.debug("Photo sent")
            os.remove(photo_name)
            time.sleep(1)
        except FileNotFoundError:
            logging.info("Photo wasn't found before sending message")
            continue

    # Write latest post time to file
    file = open('time.txt', 'w')
    file.write(str(time.mktime(datetime.datetime.strptime(
        f.entries[0].published, "%a, %d %b %Y %X %z").timetuple())))
    file.close()

while True:
    main()
    logging.info("Script went to sleep")
    time.sleep(30)
