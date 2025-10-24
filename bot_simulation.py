import os
import json
import time
import datetime
import asyncio
from telegram import (
    Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, CallbackQueryHandler
)

# -------------------- CONFIG --------------------
TOKEN = "8144184163:AAFoXga0moJqidy-uWLSKsdY890xub1oNEA"      # Replace with your bot token
ADMIN_ID = 8301422296              # Replace with your Telegram ID
CHANNEL_USERNAME = "unlimitedsms1" # Your channel username (without @)
CHANNEL_LINK = "https://t.me/unlimitedsms1"

DATA_FILE = "data.json"
START_NUMBER = 11000
COOLDOWN_SECONDS = 10 * 60  # 10 minutes

awaiting_number = set()


# -------------------- HELPERS --------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        data = {}
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_or_create_serial(user_id, data):
    user_id_str = str(user_id)
    if user_id_str not in data or not isinstance(data[user_id_str], dict):
        data[user_id_str] = {
            "serial": START_NUMBER + len(data) + 1,
            "verified1": False,
            "verified2": False,
            "last_attack": 0
        }
        save_data(data)
        return data[user_id_str]["serial"]

    if "serial" not in data[user_id_str]:
        data[user_id_str]["serial"] = START_NUMBER + len(data) + 1
        save_data(data)
    return data[user_id_str]["serial"]


def set_verified(user_id, step, value=True):
    data = load_data()
    user_data = data.get(str(user_id), {})
    if step == 1:
        user_data["verified1"] = value
    elif step == 2:
        user_data["verified2"] = value
    data[str(user_id)] = user_data
    save_data(data)


def is_verified(user_id):
    data = load_data()
    user_data = data.get(str(user_id), {})
    return user_data.get("verified1", False) and user_data.get("verified2", False)


def is_on_cooldown(user_id, data):
    key = str(user_id)
    cooldowns = data.get("cooldowns", {})
    if key in cooldowns:
        expire_ts = cooldowns[key]
        now = time.time()
        if now < expire_ts:
            return True, int(expire_ts - now)
    return False, 0


def set_cooldown(user_id, data, seconds=COOLDOWN_SECONDS):
    data.setdefault("cooldowns", {})
    data["cooldowns"][str(user_id)] = int(time.time() + seconds)
    save_data(data)


async def notify_admin(context: ContextTypes.DEFAULT_TYPE, user_id: int, serial: int, user_message: str, username: str = ""):
    username_text = f"@{username}" if username else "N/A"
    message = (
        f"📩 New user reply:\n\n"
        f"🆔 Account ID: {serial}\n"
        f"User ID: {user_id}\n"
        f"Username: {username_text}\n\n"
        f"📞 <code>{user_message}</code>"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=message, parse_mode="HTML")


# -------------------- BOT HANDLERS --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = load_data()
    get_or_create_serial(user_id, data)
    user_data = data[str(user_id)]

    # Step 1 verification
    if not user_data.get("verified1"):
        await update.message.reply_text("শিরায় শিরায় রক্ত _______ ভাইয়ের বক্ত")
        return

    # Step 2 verification
    if not user_data.get("verified2"):
        keyboard = [
            [InlineKeyboardButton("Join Channel", url=CHANNEL_LINK)],
            [InlineKeyboardButton("Joined try now", callback_data="check_joined")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("👉এই Channel এ join করুন bot টি ব্যাবহার করতে", reply_markup=reply_markup)
        return

    # If fully verified → show menu
    await show_main_menu(update)


async def show_main_menu(update: Update):
    keyboard = [["⚜️ Account", "👉 sms মাইর"], ["⚙️ Setting"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    data = load_data()
    user_id = update.effective_user.id
    serial = get_or_create_serial(user_id, data)
    welcome_text = (
        f"⛔ Hello পাপী বান্দা 😈\n"
        f"দিনে রাতে SMS এর মাইর দিতে এই bot এর সাথে যুক্ত থাকুন 💥\n\n"
        f"🆔 আপনার একাউন্ট আইডি: {serial}"
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or ""
    text = update.message.text.strip()
    data = load_data()

    # Ensure user data exists
    if str(user_id) not in data:
        get_or_create_serial(user_id, data)
    user_data = data[str(user_id)]

    # Step 1 verification
    if not user_data.get("verified1"):
        if text.lower() == "জাহিদুল":
            set_verified(user_id, 1, True)
            keyboard = [
                [InlineKeyboardButton("Join Channel", url=CHANNEL_LINK)],
                [InlineKeyboardButton("Joined try now", callback_data="check_joined")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "✅ Verification 1 Complete!\n\n👉এই Channel এ join করুন bot টি ব্যাবহার করতে",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text("❌ ভুল উত্তর! আবার চেষ্টা করুন।\n\nশিরায় শিরায় রক্ত _______ ভাইয়ের বক্ত")
        return

    # Step 2 verification
    if not user_data.get("verified2"):
        keyboard = [
            [InlineKeyboardButton("Join Channel", url=CHANNEL_LINK)],
            [InlineKeyboardButton("Joined try now", callback_data="check_joined")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("👉এই Channel এ join করুন bot টি ব্যাবহার করতে", reply_markup=reply_markup)
        return

    # After verification → normal bot usage
    if user_id in awaiting_number:
        candidate = text.replace(" ", "")
        serial = get_or_create_serial(user_id, data)

        if candidate.isdigit() and len(candidate) == 11:
            on_cd, remaining = is_on_cooldown(user_id, data)
            if on_cd:
                mins, secs = divmod(remaining, 60)
                await update.message.reply_text(f"⏳ Cooldown active. Wait {mins}m {secs}s.")
                awaiting_number.discard(user_id)
                return

            await notify_admin(context, user_id, serial, candidate, username)
            set_cooldown(user_id, data)
            awaiting_number.discard(user_id)
            await update.message.reply_text("🌚 Successfully requested (10-min cooldown active)")
        else:
            await update.message.reply_text("❌ Invalid number. Send ১১-digit mobile number.")
        return

    # Menu button handling
    if text == "⚜️ Account":
        serial = get_or_create_serial(user_id, data)
        await update.message.reply_text(f"📂 Account Details:\n\n🆔 Account ID: {serial}")
    elif text == "👉 sms মাইর":
        on_cd, remaining = is_on_cooldown(user_id, data)
        if on_cd:
            mins, secs = divmod(remaining, 60)
            await update.message.reply_text(f"⏳ Cooldown active. Wait {mins}m {secs}s.")
            return
        awaiting_number.add(user_id)
        await update.message.reply_text("যারে sms মাইর দিতে চান তার ১১ ডিজিট মোবাইল নম্বর টি দিন")
    elif text == "⚙️ Setting":
        await update.message.reply_text("⚙️ Settings Section")
    else:
        serial = get_or_create_serial(user_id, data)
        await notify_admin(context, user_id, serial, text, username)
        await update.message.reply_text("✅ Message received")


# -------------------- CHANNEL JOIN CHECK --------------------
async def check_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    try:
        member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        if member.status in ["member", "administrator", "creator"]:
            set_verified(user_id, 2, True)
            await query.message.edit_text("✅ Channel joined successfully! Verification complete ✅")
            fake_update = Update(update.update_id, message=query.message)
            await show_main_menu(fake_update)
        else:
            await query.answer("❌ You are not Joined yet click on 'Join channel'", show_alert=True)
    except:
        await query.answer("⚠️ Bot needs to be admin in the channel to verify membership.", show_alert=True)


# -------------------- MAIN --------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(check_joined, pattern="check_joined"))

    print("✅ Bot is running... Press CTRL+C to stop.")
    asyncio.run(app.run_polling())


if __name__ == "__main__":
    main()

