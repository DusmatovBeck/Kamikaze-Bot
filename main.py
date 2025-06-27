import asyncio
import json
import random
from pathlib import Path
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode

API_TOKEN = "8165348581:AAEaLQ2S2fPGvlevaXhwieXtcqNikjSWyI8"

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

USER_DATA_PATH = Path("data")

def get_user_file(user_id):
    return USER_DATA_PATH / f"{user_id}.json"

def load_user_data(user_id):
    file = get_user_file(user_id)
    if file.exists():
        with open(file, "r") as f:
            return json.load(f)
    else:
        return {"history": [], "stats": {"1": [0, 0], "2": [0, 0], "3": [0, 0], "4": [0, 0], "5": [0, 0]}}

def save_user_data(user_id, data):
    with open(get_user_file(user_id), "w") as f:
        json.dump(data, f)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("👋 Salom! Kamikaze Signal Botga xush kelibsiz!\n\n🎯 /signal - signal olish\n📊 /stats - statistikangiz\n🕓 /history - so‘nggi 10 ta signal")

@dp.message(Command("signal"))
async def signal(message: Message):
    user_id = str(message.from_user.id)
    data = load_user_data(user_id)
    signal_number = random.randint(1, 5)
    data["history"].append({"signal": signal_number, "feedback": None})
    if len(data["history"]) > 10:
        data["history"].pop(0)
    save_user_data(user_id, data)
    await message.answer(f"🎯 Signal: <b>{signal_number}</b>\n\nJavob: /true yoki /false")

@dp.message(Command("true"))
async def correct(message: Message):
    user_id = str(message.from_user.id)
    data = load_user_data(user_id)
    if data["history"] and data["history"][-1]["feedback"] is None:
        number = str(data["history"][-1]["signal"])
        data["stats"][number][0] += 1
        data["history"][-1]["feedback"] = True
        save_user_data(user_id, data)
        await message.answer("✅ To‘g‘ri deb belgilandi.")
    else:
        await message.answer("⚠️ Avval signal oling yoki fikr allaqachon bildirilgan.")

@dp.message(Command("false"))
async def incorrect(message: Message):
    user_id = str(message.from_user.id)
    data = load_user_data(user_id)
    if data["history"] and data["history"][-1]["feedback"] is None:
        number = str(data["history"][-1]["signal"])
        data["stats"][number][1] += 1
        data["history"][-1]["feedback"] = False
        save_user_data(user_id, data)
        await message.answer("❌ Noto‘g‘ri deb belgilandi.")
    else:
        await message.answer("⚠️ Avval signal oling yoki fikr allaqachon bildirilgan.")

@dp.message(Command("stats"))
async def stats(message: Message):
    user_id = str(message.from_user.id)
    data = load_user_data(user_id)
    msg = "📊 Statistikangiz:\n"
    total_correct = total_wrong = 0
    for num, (correct, wrong) in data["stats"].items():
        total_correct += correct
        total_wrong += wrong
        msg += f"{num}: ✅ {correct} | ❌ {wrong}\n"
    msg += f"\nUmumiy: ✅ {total_correct} | ❌ {total_wrong}"
    await message.answer(msg)

@dp.message(Command("history"))
async def history(message: Message):
    user_id = str(message.from_user.id)
    data = load_user_data(user_id)
    msg = "🕓 Oxirgi 10 signal:\n"
    for entry in data["history"]:
        feedback = "✅" if entry["feedback"] is True else ("❌" if entry["feedback"] is False else "⏳")
        msg += f"{entry['signal']} {feedback}\n"
    await message.answer(msg)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())