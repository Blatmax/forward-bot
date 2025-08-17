import asyncio
import json
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))  # ID группы (с минусом)

# файл для хранения связок канал->тема
FILE = os.getenv("BINDINGS_PATH", "bindings.json")
os.makedirs(os.path.dirname(FILE) or ".", exist_ok=True)

# загрузка связок
if os.path.exists(FILE):
    with open(FILE, "r", encoding="utf-8") as f:
        CHANNEL_TO_TOPIC = json.load(f)
else:
    CHANNEL_TO_TOPIC = {}

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()


def save_bindings():
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(CHANNEL_TO_TOPIC, f, ensure_ascii=False, indent=2)


# команда /bind
@dp.message(Command("bind"))
async def bind_channel_topic(message: Message):
    parts = message.text.split()
    if len(parts) != 3:
        await message.reply("Используй: /bind <channel_id> <topic_id>")
        return

    channel_id = int(parts[1])
    topic_id = int(parts[2])

    CHANNEL_TO_TOPIC[str(channel_id)] = topic_id
    save_bindings()
    await message.reply(f"✅ Связка добавлена:\nКанал {channel_id} → Тема {topic_id}")


# обработка постов из канала
@dp.channel_post()
async def forward_channel_post(message: Message):
    topic_id = CHANNEL_TO_TOPIC.get(str(message.chat.id))
    if not topic_id:
        return

    kwargs = {"message_thread_id": topic_id}

    if message.text or message.caption:
        text = message.text or message.caption
    else:
        text = None

    if message.photo:
        await bot.send_photo(GROUP_ID, message.photo[-1].file_id, caption=text, **kwargs)
    elif message.video:
        await bot.send_video(GROUP_ID, message.video.file_id, caption=text, **kwargs)
    elif message.document:
        await bot.send_document(GROUP_ID, message.document.file_id, caption=text, **kwargs)
    elif message.audio:
        await bot.send_audio(GROUP_ID, message.audio.file_id, caption=text, **kwargs)
    elif message.voice:
        await bot.send_voice(GROUP_ID, message.voice.file_id, caption=text, **kwargs)
    elif message.sticker:
        await bot.send_sticker(GROUP_ID, message.sticker.file_id, **kwargs)
    else:
        await message.send_copy(GROUP_ID, **kwargs)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
