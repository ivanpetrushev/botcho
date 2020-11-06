import asyncio
import datetime
import discord
import ctypes
import ctypes.util
from reddit import load_fun_pool
from misc import get_water
import time
from random import choice
from lightning import LightningNotifier

TARGET_VOICE_CHANNEL = 'General'
TARGET_STORMS_CHANNEL = 'notifications-storms'
BELL_AUDIO_FILENAME = 'bells-neli-7s.mp3'
PETEL_AUDIO_FILENAME = 'petel-iliyana-7s.mp3'


class MyClient(discord.Client):
    fun_link_pool = []
    voice_client = None
    bells_last_played_ts = None
    petel_last_played_ts = None

    async def join_voice_channel(self):
        selected_channel = None
        for ch in client.get_all_channels():
            if ch.name == TARGET_VOICE_CHANNEL:
                selected_channel = ch
        if not selected_channel:
            print(f"Cant find desired voice channel: {TARGET_VOICE_CHANNEL}")
            return
        self.voice_client = await discord.VoiceChannel.connect(selected_channel, timeout=10)
        print('Voice connected')
    
    def after_play_bells(self, error):
        # after= can't execute directly coroutines. asyncio can
        coro = self.voice_client.disconnect()
        runner = asyncio.run_coroutine_threadsafe(coro, client.loop)
        try:
            runner.result()
        except:
            # an error happened sending the message
            pass

    def after_play_petel(self, error):
        # after= can't execute directly coroutines. asyncio can
        coro = self.voice_client.disconnect()
        runner = asyncio.run_coroutine_threadsafe(coro, client.loop)
        try:
            runner.result()
        except:
            # an error happened sending the message
            pass

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        # probably load this only if needed. Reddit tends to throw 429 Too many requests on frequent requests
        # self.link_pool = load_fun_pool()

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))
        # print(message)
        if message.content.startswith('!fun'):
            if len(self.fun_link_pool) == 0:
                self.fun_link_pool = load_fun_pool()
            if len(self.fun_link_pool) == 0:
                my_msg = 'Свърши fun-а. Сядай да бачкаш :P'
            else:
                my_msg = self.fun_link_pool.pop()
            await message.channel.send(my_msg)

        if message.content.startswith('!weather'):
            url = 'http://cap.weathermod-bg.eu/GCDCAP_G.jpg?nc=' + \
                str(time.time())
            await message.channel.send(url)

        if message.content.startswith('!water'):
            gfycat_url = get_water()
            await message.channel.send("Пийте вода! :)")
            await message.channel.send(gfycat_url)

        if message.content.startswith('!kambana'):
            hour = int(datetime.datetime.now().strftime('%-H'))
            if hour < 16:
                print(f"Requested !kambana before 16h. Current hour: {hour}")
                return
            now_ts = int(datetime.datetime.now().timestamp())
            if self.bells_last_played_ts and self.bells_last_played_ts + 600 > now_ts:
                print(f"Requested !kambana too soon, last played in {self.bells_last_played_ts}")
                return
            self.bells_last_played_ts = now_ts
            audio_source = discord.FFmpegPCMAudio(BELL_AUDIO_FILENAME)
            await self.join_voice_channel()
            print(f'Playing bells at {self.bells_last_played_ts}')
            if not self.voice_client.is_playing():
                self.voice_client.play(audio_source, after=self.after_play_bells)

        if message.content.startswith('!petel'):
            hour = int(datetime.datetime.now().strftime('%-H'))
            if hour > 13:
                print(f"Requested !petel after 13h. Current hour: {hour}")
                return
            now_ts = int(datetime.datetime.now().timestamp())
            if self.petel_last_played_ts and self.petel_last_played_ts + 600 > now_ts:
                print(f"Requested !petel too soon, last played in {self.petel_last_played_ts}")
                return
            self.petel_last_played_ts = now_ts
            audio_source = discord.FFmpegPCMAudio(PETEL_AUDIO_FILENAME)
            await self.join_voice_channel()
            print(f'Playing petel at {self.petel_last_played_ts}')
            if not self.voice_client.is_playing():
                self.voice_client.play(audio_source, after=self.after_play_petel)


        if message.content.startswith('!help'):
            my_msg = "Команди: \n" \
                     "!fun - смешна картинка (не винаги)\n" \
                     "!weather - радара за градушките\n" \
                     "!water - пийте вода\n" \
                     "!kambana - бием камбаната и си отиваме"
            await message.channel.send(my_msg)


async def remind_water():
    await client.wait_until_ready()
    selected_channel = None
    target_channel = 'office1'
    for ch in client.get_all_channels():
        if ch.name == target_channel:
            selected_channel = ch
    print('remind_water: Selected channel:', selected_channel)

    while not client.is_closed():
        hour = int(datetime.datetime.now().strftime('%-H'))
        day_of_week = int(datetime.datetime.now().strftime('%w'))  # 0 is Sunday and 6 is Saturday
        print(f"remind_water check: hour {hour} day_of_week {day_of_week}")
        if hour in [10, 13, 15] and 0 < day_of_week < 6:
            gfycat_url = get_water()
            water_messages = ["Който пие вода - не умира", "Една вода, моля", "Водна чаша, пълна с ... вода!", "Водата му е майката",
                "Не забравяме водата, нали? :)", "Може да съм бот, ама и аз пия вода :P", "Келнер! Сипи една вода!", "Дай една вода",
                "Студена вода, или студена бира?", "Ако се чудиш какво да правиш, що не пиеш една вода?", "3.. 2.. 1.. идва водата :)"]
            await selected_channel.send(choice(water_messages))
            await selected_channel.send(gfycat_url)
        await asyncio.sleep(3600)


async def remind_lightning():
    ln = LightningNotifier()
    await client.wait_until_ready()
    selected_channel = None
    for ch in client.get_all_channels():
        if ch.name == TARGET_STORMS_CHANNEL:
            selected_channel = ch
    print('remind_lightning: Selected channel:', selected_channel)

    while not client.is_closed():
        msg = ln.notify()
        if msg:
            await selected_channel.send(msg)
        await asyncio.sleep(300)

opusname = ctypes.util.find_library('opus')
discord.opus.load_opus(opusname)

token = open("token.txt", "r").read()
client = MyClient()
# client.loop.create_task(remind_water()) # disabling water messages due to gfycat returning stupid results
client.loop.create_task(remind_lightning())
client.run(token)
