import asyncio
import datetime
import discord
from reddit import load_fun_pool
from misc import get_water
import time


class MyClient(discord.Client):
    fun_link_pool = []

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        # probably load this only if needed. Reddit tends to throw 429 Too many requests on frequent requests
        # self.link_pool = load_fun_pool()

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))
        print(message)
        if message.content.startswith('!fun'):
            if len(self.fun_link_pool) == 0:
                self.fun_link_pool = load_fun_pool()
            if len(self.fun_link_pool) == 0:
                my_msg = 'Свърши fun-а. Сядай да бачкаш :P'
            else:
                my_msg = self.fun_link_pool.pop()
            await message.channel.send(my_msg)
        if message.content.startswith('!weather'):
            url = 'http://cap.weathermod-bg.eu/GCDCAP_G.jpg?nc=' + str(time.time())
            await message.channel.send(url)
        if message.content.startswith('!water'):
            gfycat_url = get_water()
            await message.channel.send("Пийте вода! :)")
            await message.channel.send(gfycat_url)
        if message.content.startswith('!help'):
            my_msg = "Команди: \n" \
                     "!fun - смешна картинка (не винаги)\n" \
                     "!weather - радара за градушките\n" \
                     "!water - пийте вода"
            await message.channel.send(my_msg)


async def remind_water():
    await client.wait_until_ready()
    selected_channel = None
    target_channel = 'general'
    for ch in client.get_all_channels():
        if ch.name == target_channel:
            selected_channel = ch
    print('remind_water: Selected channel:', selected_channel)

    while not client.is_closed():
        hour = int(datetime.datetime.now().strftime('%-H'))
        if hour in [10, 13, 15]:
            gfycat_url = get_water()
            await selected_channel.send("Пийте вода! :)")
            await selected_channel.send(gfycat_url)
        await asyncio.sleep(3600)


token = open("token.txt", "r").read()
client = MyClient()
client.loop.create_task(remind_water())
client.run(token)
