# Server Monitor Bot

Telegram-бот для мониторинга Linux-сервера.

## Команды
- `/status` — имя сервера, время работы, память, диск
- `/id` — узнать свой Telegram ID
- `/db` — состояние PostgreSQL: версия, подключения, размер баз

## Установка
1. `python3 -m venv venv && source venv/bin/activate`
2. `pip install -r requirements.txt`
3. Скопировать `.env.example` в `.env` и вписать токен и свой ID
4. `python3 bot.py`
