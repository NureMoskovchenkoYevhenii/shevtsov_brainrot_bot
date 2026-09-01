import asyncio
import json
import os
import aiohttp
import xml.etree.ElementTree as ET
from aiogram import Bot
from aiohttp import web
from config import BOT_TOKEN, CHAT_ID, CHANNELS, CHECK_INTERVAL

bot = Bot(token=BOT_TOKEN)
DB_FILE = "sent_videos.json"

def load_sent_videos() -> list:
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_sent_videos(videos: list):
    with open(DB_FILE, "w") as f:
        json.dump(videos, f)

async def get_latest_video_id(channel_id: str) -> str:
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return ""
                xml_data = await response.text()
        except Exception:
            return ""
    try:
        root = ET.fromstring(xml_data)
        namespaces = {
            "ns": "http://www.w3.org/2005/Atom",
            "yt": "http://www.youtube.com/xml/schemas/2015"
        }
        entry = root.find("ns:entry", namespaces)
        if entry is not None:
            video_id_element = entry.find("yt:videoId", namespaces)
            if video_id_element is not None:
                return video_id_element.text
    except Exception:
        pass
    return ""

async def check_updates():
    print("Запуск проверки обновлений...")
    sent_videos = load_sent_videos()
    first_run = len(sent_videos) == 0
    print(f"Загружено ранее отправленных видео: {len(sent_videos)}")
    
    for channel_id in CHANNELS:
        print(f"Запрос последнего видео для канала {channel_id}...")
        video_id = await get_latest_video_id(channel_id)
        print(f"Получен ID видео: {video_id}")
        
        if not video_id:
            print("Не удалось получить ID видео для этого канала")
            continue

        if video_id not in sent_videos:
            print(f"Обнаружено новое видео {video_id}, добавляем в список")
            sent_videos.append(video_id)
            if True:
            #if not first_run:
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                try:
                    print(f"Отправка сообщения в группу {CHAT_ID}...")
                    await bot.send_message(chat_id=CHAT_ID, text=f"Новое видео на канале!\n{video_url}")
                    print("Сообщение успешно отправлено!")
                except Exception as e:
                    print(f"Ошибка отправки сообщения: {e}")
        else:
            print(f"Видео {video_id} уже есть в базе данных, отправка пропущена")
            
    save_sent_videos(sent_videos)
    print("Проверка обновлений завершена. Ожидание следующего цикла...")

async def handle_health_check(request):
    return web.Response(text="Бот активен")

async def main():
    app = web.Application()
    app.router.add_get("/", handle_health_check)
    
    port = int(os.environ.get("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Веб-сервер запущен на порту {port}")

    try:
        while True:
            await check_updates()
            await asyncio.sleep(CHECK_INTERVAL)
    finally:
        await bot.session.close()
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())