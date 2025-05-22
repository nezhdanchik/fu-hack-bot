import asyncio
import logging
import os
from typing import TypedDict

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types.message import Message
from dotenv import load_dotenv

from src.llm_connector import request_llm, final_request_llm

load_dotenv()
BOT_TOKEN = os.environ["BOT_TOKEN"]
MAX_MESSAGE_COUNT = 10

class TgUserData(TypedDict):
    num_message: int
    state: str


users: dict[int, TgUserData] = {}


async def main():
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    bot = Bot(token=BOT_TOKEN, parse_mode=None)
    logging.basicConfig(level=logging.INFO)

    @dp.channel_post(Command(commands=["start"]))
    async def start(message: Message) -> None:
        print(f"User started bot")
        users[message.chat.id] = TgUserData(
            num_message=0,
            state="active",
        )

    @dp.channel_post(F.text)
    async def repl(message: Message) -> None:
        cid = message.chat.id
        if cid not in users or users[cid]["state"] != "active":
            return
        human_message = message.text
        users[cid]["num_message"] += 1
        remaining_count = MAX_MESSAGE_COUNT - users[cid]["num_message"]
        if remaining_count >= 1:
            r = await request_llm(human_message, remaining_count)
            await message.answer(r)
        else:
            users[message.chat.id] = TgUserData(
                num_message=0,
                state="finished",
            )
            r = await final_request_llm(human_message)
            await message.answer(r)

    @dp.channel_post(~F.text)
    async def empty(message: Message) -> None:
        await message.answer("Бот принимает только текст")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())