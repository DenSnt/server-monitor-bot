import asyncio
import os
import subprocess

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))   # твой ID из файла .env
dp = Dispatcher()


def run(command: list[str]) -> str:
    """Выполняет команду Linux и возвращает её вывод в виде текста."""
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout.strip()


def is_admin(message: Message) -> bool:
    """Проверяет, что пишет именно владелец бота."""
    return message.from_user.id == ADMIN_ID


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет! Я бот-мониторинг сервера.\n"
        "/status — состояние сервера\n"
        "/id — узнать свой Telegram ID"
    )


@dp.message(Command("id"))
async def my_id(message: Message):
    await message.answer(f"Твой Telegram ID: {message.from_user.id}")


@dp.message(Command("status"))
async def status(message: Message):
    if not is_admin(message):
        await message.answer("Нет доступа.")
        return

    hostname = run(["hostname"])
    uptime = run(["uptime", "-p"])
    memory = run(["free", "-h"])
    disk = run(["df", "-h", "/"])

    text = (
        f"🖥 Сервер: {hostname}\n"
        f"⏱ Работает: {uptime}\n\n"
        f"💾 Память:\n<pre>{memory}</pre>\n"
        f"📀 Диск:\n<pre>{disk}</pre>"
    )
    await message.answer(text, parse_mode="HTML")


async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
