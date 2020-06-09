from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
import random


def scrape_sub(sub_name):
    out = []
    print('Scraping sub', sub_name)
    time.sleep(2)
    url = 'https://old.reddit.com/r/' + sub_name + '/'
    fp = urlopen(url)
    contents = fp.read()
    soup = BeautifulSoup(contents, "html.parser")

    for item in soup.select('div[data-author-fullname]'):
        print('item', item.attrs['data-url'])
        img_url = item.attrs['data-url']
        if 'i.redd.it' in img_url or 'imgur' in img_url:
            out.append(img_url)
    return out


def load_fun_pool():
    out = []
    subs = ['funny', 'ProgrammerHumor']
    for sub in subs:
        for item in scrape_sub(sub):
            out.append(item)
    random.shuffle(out)
    print(f'loading pool with {len(out)} items:', out)
    return out
