import discord
from urllib.request import urlopen
from bs4 import BeautifulSoup
import random
import time
import json
import asyncio
import datetime


def get_water():
    api_key = open("gfy_token.txt", "r").read()
    url = 'http://api.giphy.com/v1/gifs/random?tag=water&api_key=' + api_key
    fp = urlopen(url)
    contents = json.load(fp)
    return contents['data']['url']


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


def load_pool():
    out = []
    subs = ['funny', 'ProgrammerHumor']
    for sub in subs:
        for item in scrape_sub(sub):
            out.append(item)
    random.shuffle(out)
    print(f'loading pool with {len(out)} items:', out)
    return out


class MyClient(discord.Client):
    link_pool = []

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        self.link_pool = load_pool()

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))
        print(message)
        if message.content.startswith('!fun'):
            if len(self.link_pool) == 0:
                self.link_pool = load_pool()
            my_msg = self.link_pool.pop()
            await message.channel.send(my_msg)
        if message.content.startswith('!test'):
            await message.channel.send('https://i.redd.it/b61u4gk752351.jpg')
        if message.content.startswith('!water'):
            gfycat_url = get_water()
            await message.channel.send("Пийте вода! :)")
            await message.channel.send(gfycat_url)


async def remind_water():
    await client.wait_until_ready()
    selected_channel = None
    # target_channel = 'general'
    target_channel = 'test'
    for ch in client.get_all_channels():
        if ch.name == target_channel:
            selected_channel = ch
    print('Selected channel', selected_channel)

    while not client.is_closed():
        hour = int(datetime.datetime.now().strftime('%-H'))
        if 9 < hour < 16 and hour % 3 == 0:
            gfycat_url = get_water()
            await selected_channel.send("Пийте вода! :)")
            await selected_channel.send(gfycat_url)
        await asyncio.sleep(3600)


token = open("token.txt", "r").read()
client = MyClient()
client.loop.create_task(remind_water())
client.run(token)
