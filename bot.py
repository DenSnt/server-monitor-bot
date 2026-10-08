import asyncio
import os
import subprocess

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
dp = Dispatcher()


def run(command: list[str]) -> str:
    """Выполняет команду Linux и возвращает её вывод в виде текста."""
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout.strip()


def psql(query: str) -> str:
    """Выполняет SQL-запрос к PostgreSQL и возвращает результат."""
    return run(["psql", "-d", "postgres", "-tAc", query])


def is_admin(message: Message) -> bool:
    """Проверяет, что пишет именно владелец бота."""
    return message.from_user.id == ADMIN_ID


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет! Я бот-мониторинг сервера.\n"
        "/status — состояние сервера\n"
        "/db — состояние PostgreSQL\n"
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


@dp.message(Command("db"))
async def db(message: Message):
    if not is_admin(message):
        await message.answer("Нет доступа.")
        return

    ready = subprocess.run(["pg_isready"], capture_output=True)
    if ready.returncode != 0:
        await message.answer("🔴 PostgreSQL не принимает подключения!")
        return

    version = psql("SHOW server_version;")
    connections = psql(
        "SELECT count(*) FROM pg_stat_activity "
        "WHERE backend_type = 'client backend';"
    )
    sizes = psql(
        "SELECT datname || ': ' || pg_size_pretty(pg_database_size(datname)) "
        "FROM pg_database WHERE NOT datistemplate;"
    )

    text = (
        f"🟢 PostgreSQL работает\n"
        f"Версия: {version}\n"
        f"Активных подключений: {connections}\n\n"
        f"📦 Размер баз:\n<pre>{sizes}</pre>"
    )
    await message.answer(text, parse_mode="HTML")


async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
