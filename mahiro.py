import json
import logging
import os
import asyncio
import aiohttp
import youtube_dl

from concurrent.futures.thread import ThreadPoolExecutor
from aiogram import Bot, Dispatcher, types
from aiogram.utils import exceptions, executor
from aiogram.dispatcher.filters import Command

import config

# Inisialisasi bot, dispathcer, dan loop asyncio
logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)
loop = asyncio.get_event_loop()

# Membuat pool thread
executor = ThreadPoolExecutor(max_workers=2)

# Membuat cache data
cache = {}

# Fungsi untuk menghapus cache
async def clear_cache():
    await asyncio.sleep(config.CACHE_TIME)
    cache.clear()

# Command /ping untuk menguji kecepatan respon bot
@dp.message_handler(commands=['ping'])
async def ping_pong(message: types.Message):
    start = time.time()
    msg = await bot.send_message(message.chat.id, 'Pong!')
    end = time.time()
    await bot.edit_message_text(f'Pong! {end - start} detik', message.chat.id, msg.message_id)

# Command /music untuk mengambil audio dari video YouTube dan mengirimkannya ke Telegram
@dp.message_handler(Command('music'))
async def music(message: types.Message):
    try:
        # Parsing video URL
        url = message.text.split(' ')[1]

        # Mendownload audio dari video YouTube menggunakan YoutubeDL
        loop.run_in_executor(executor, download_audio, url)

        # Membuka file audio yang telah diunduh
        with open('audio.mp3', 'rb') as audio:
            # Mengirim file audio ke pengguna
            await bot.send_audio(message.chat.id, audio, title='Music')

    except Exception as e:
        logging.exception(e)
        await bot.send_message(message.chat.id, 'Gagal mengunduh audio')

# Fungsi untuk mengunduh audio dari video YouTube
def download_audio(url):
    # Cek apakah cache telah tersedia
    if url in cache:
        return cache[url]

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio.mp3',
        'noplaylist': True,
        'quiet': True
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Menambah data ke cache
    cache[url] = None

    return None

# Command /help untuk menampilkan seluruh fitur bot
@dp.message_handler(commands=['help'])
async def help_message(message: types.Message):
    help_text = 'Daftar perintah yang tersedia:\n'
    help_text += '/ping - Tes kecepatan respon bot\n'
    help_text += '/music <yt link> - Mengunduh audio dari video YouTube\n'
    await bot.send_message(message.chat.id, help_text)

# Jalankan cache secara periodik
loop.create_task(clear_cache())

# Jalankan bot
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

