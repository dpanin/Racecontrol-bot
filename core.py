""" This module checks for new posts and then gets the main text and image."""
from contextlib import contextmanager
import urllib.response
import urllib.request
import datetime
import shutil
import signal
import time
import feedparser
from bs4 import BeautifulSoup


FEED_URL = ("http://racecontrol.me/site/rss")
NET_TIMEOUT = 10

#FUNCS

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


def image_download(entry_number):
    """Download images from RSS feed"""
    desc = f.entries[entry_number].description
    soup_desc = BeautifulSoup(desc, "lxml")
    # Download file and save under 'i' name
    # Add timeout exception
    filename = ""
    filename = filename.join([str(entry_number), ".jpeg"])
    with urllib.request.urlopen(soup_desc.img['src']) as response, \
            open(filename, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    IMAGES.append(i)

#MAIN

while True:
    print('Begin processing the feed...')

    # Defining variables
    LINKS = []
    IMAGES = []

    try:
        with timeout_sec(NET_TIMEOUT):
            f = feedparser.parse(FEED_URL)
    except TimeoutException:
        print("ERROR: Timeout!")
        continue

    i = 0

    FILE = open('time.txt', 'r')
    LAST_DATE = float(FILE.read())
    FILE.close()

    # Finding newer posts by comparing time
    for i in f['entries']:
        converted_time = time.mktime(datetime.datetime.strptime(
            i.published, "%a, %d %b %Y %X %z").timetuple())
        if converted_time > LAST_DATE:
            LINKS.append(i.link)
        else:
            break

    # Get text from news
    for i in reversed(LINKS):
        post_page = urllib.request.urlopen(i)
        # Add timeout exception
        html = post_page.read()
        soup = BeautifulSoup(html, "lxml")

        post = soup.find("div", class_="post-news-lead")
        post = post.text
        post = post.replace(u'\xa0', u' ')
        # For debugging
        print(post)

    # Write latest post time to file
    FILE = open('time.txt', 'w')
    FILE.write(str(time.mktime(datetime.datetime.strptime(
        f.entries[0].published, "%a, %d %b %Y %X %z").timetuple())))
    FILE.close()

    print("Going to sleep for 30 seconds")
    time.sleep(30)
