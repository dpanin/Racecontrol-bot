import feedparser
from contextlib import contextmanager
from bs4 import BeautifulSoup
import urllib.response
import urllib.request
import datetime
import shutil
import signal
import time

feed_url = ("http://racecontrol.me/site/rss")
net_timeout = 10
latest_post = "latest_post.txt"


class TimeoutException(Exception):
    pass


@contextmanager
def timeout_sec(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException(Exception("Timed out!"))
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


def image_download(id):
    desc = f.entries[id].description
    soup_desc = BeautifulSoup(desc, "lxml")
    #
    soup_desc.img['src']
    # Download file and save under 'i' name
    # Add timeout exception
    filename = ""
    filename = filename.join([str(id), ".jpeg"])
    with urllib.request.urlopen(soup_desc.img['src']) as response, open(filename, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    images.append(i)

while True:
    print('Begin processing the feed...')

    # Defining variables
    links = []
    images = []

    try:
        with timeout_sec(net_timeout):
            f = feedparser.parse(feed_url)
    except TimeoutException:
        print("ERROR: Timeout!")
        continue

    i = 0

    file = open('time.txt', 'r')
    last_date = float(file.read())
    file.close()

    # Finding newer posts by comparing time
    for i in f['entries']:
        converted_time = time.mktime(datetime.datetime.strptime(
            i.published, "%a, %d %b %Y %X %z").timetuple())
        if converted_time > last_date:
            links.append(i.link)
        else:
            break

    # Get text from news
    for i in reversed(links):
        response = urllib.request.urlopen(i)
        # Add timeout exception
        html = response.read()
        soup = BeautifulSoup(html, "lxml")

        post = soup.find("div", class_="post-news-lead")
        post = post.text
        post = post.replace(u'\xa0', u' ')
        # For debugging
        print(post)

    # Write latest post time to file
    file = open('time.txt', 'w')
    file.write(str(time.mktime(datetime.datetime.strptime(
            f.entries[0].published, "%a, %d %b %Y %X %z").timetuple())))
    file.close()

    print("Going to sleep for 30 seconds")
    time.sleep(30)
