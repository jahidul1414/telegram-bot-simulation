# bot_simulation.py
import os, json, time, datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Use environment variable for token (Render will add this securely)
TOKEN = os.getenv("8144184163:AAFoXga0moJqidy-uWLSKsdY890xub1oNEA")

ADMIN_ID = 8301422296          # <-- Replace with your Telegram numeric ID
DATA_FILE = "data.json"
START_NUMBER = 11000           # account IDs start at 11001
COOLDOWN_SECONDS = 30 * 60    # 30 minutes

# in-memory tracking for users currently entering number
awaiting_number = set()


# -------------------- Helper functions --------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        data = {"users": {}, "cooldowns": {}}
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
        return data
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_or_create_serial(user_id, data):
    users = data["users"]
    if str(user_id) not in users:
        new_serial = START_NUMBER + len(users) + 1
        users[str(user_id)] = new_serial
        save_data(data)
    return users[str(user_id)]


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


async def notify_admin(context: ContextTypes.DEFAULT_TYPE, user_id: int, serial: int, username: str, user_message: str):
    """Send a message to the ADMIN_ID with user info"""
    username_text = f"@{username}" if username else "No username"
    message = (
        f"📩 New user reply received:\n\n"
        f"🆔 Account ID: {serial}\n"
        f"User ID: {user_id}\n"
        f"Username: {username_text}\n"
        f"Message: {user_message}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=message)


# -------------------- Commands --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user_id = update.message.from_user.id
    serial = get_or_create_serial(user_id, data)

    keyboard = [["⚜️ Account", "👉 sms মাইর"], ["⚙️ Setting"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    welcome_text = (
        f"⛔ Hello পাপী বান্দা 😈\n"
        f"দিনে রাতে SMS এর মাইর দিতে এই bot এর সাথে যুক্ত থাকুন 💥\n\n"
        f"🆔 আপনার একাউন্ট আইডি: {serial}"
    )

    await update.message.reply_text(welcome_text, reply_markup=reply_markup)


# -------------------- Handle user messages --------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user
    user_id = user.id
    username = user.username
    data = load_data()

    # If user is currently entering a number
    if user_id in awaiting_number:
        candidate = text.strip().replace(" ", "")
        serial = get_or_create_serial(user_id, data)

        # Send admin notification instantly
        await notify_admin(context, user_id, serial, username, candidate)

        # Check if valid 11-digit number
        if candidate.isdigit() and len(candidate) == 11:
            set_cooldown(user_id, data)
            awaiting_number.discard(user_id)
            await update.message.reply_text("🌚 Successfully requested for 5 minutes (simulation)")
        else:
            await update.message.reply_text("❌ This number is incorrect\nদয়া করে ১১ ডিজিট মোবাইল নম্বর দিন")
        return

    # Handle menu buttons
    if text == "⚜️ Account":
        serial = get_or_create_serial(user_id, data)
        await update.message.reply_text(f"📂 Your Account Details:\n\n🆔 Account ID: {serial}")
    elif text == "👉 sms মাইর":
        on_cd, remaining = is_on_cooldown(user_id, data)
        if on_cd:
            mins = remaining // 60
            secs = remaining % 60
            await update.message.reply_text(f"⏳ Cooldown active. Please wait {mins}m {secs}s before trying again.")
            return
        awaiting_number.add(user_id)
        await update.message.reply_text("যারে sms মাইর দিতে চান তার ১১ ডিজিট মোবাইল নম্বর টি দিন")
    elif text == "⚙️ Setting":
        await update.message.reply_text("⚙️ Settings Section\nYou can adjust your preferences here.")
    else:
        # Forward **any message** typed by the user to admin automatically
        serial = get_or_create_serial(user_id, data)
        await notify_admin(context, user_id, serial, username, text)
        await update.message.reply_text("✅ Your message has been received")


# -------------------- Main --------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot is running... Press CTRL+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()











