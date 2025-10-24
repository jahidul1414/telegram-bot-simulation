import json
import time
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, CallbackQueryHandler
)

# ===== CONFIG =====
TOKEN = "8144184163:AAFoXga0moJqidy-uWLSKsdY890xub1oNEA"
ADMIN_ID = 123456789  # Replace with your Telegram user ID
CHANNEL_USERNAME = "unlimitedsms1"
COOLDOWN_SECONDS = 600  # 10 minutes

# ===== DATA STORAGE =====
data = {}

# ===== UTILITIES =====
def is_on_cooldown(user_id):
    if user_id in data and "last_used" in data[user_id]:
        return (time.time() - data[user_id]["last_used"]) < COOLDOWN_SECONDS
    return False

def update_cooldown(user_id):
    if user_id not in data:
        data[user_id] = {}
    data[user_id]["last_used"] = time.time()

# ===== BOT HANDLERS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in data:
        data[user_id] = {"verified1": False, "verified2": False}

    if not data[user_id]["verified1"]:
        await update.message.reply_text("শিরায় শিরায় রক্ত _______ ভাইয়ের বক্ত")
        return

    if not data[user_id]["verified2"]:
        buttons = [
            [InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")],
            [InlineKeyboardButton("Joined try now", callback_data="check_joined")]
        ]
        await update.message.reply_text(
            "👉এই Channel এ join করুন bot টি ব্যাবহার করতে",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    await show_menu(update)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    text = update.message.text.strip()

    if user_id not in data or not data[user_id]["verified1"]:
        if text == "জাহিদুল":
            data[user_id] = {"verified1": True, "verified2": False}
            buttons = [
                [InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")],
                [InlineKeyboardButton("Joined try now", callback_data="check_joined")]
            ]
            await update.message.reply_text(
                "✅ Verification 1 complete!\n👉এই Channel এ join করুন bot টি ব্যাবহার করতে",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await update.message.reply_text("❌ ভুল উত্তর, আবার চেষ্টা করুন।")
        return

    if not data[user_id]["verified2"]:
        await update.message.reply_text("⚠️ Channel verification not complete yet!")
        return

    if is_on_cooldown(user_id):
        await update.message.reply_text("⏳ Please wait 10 minutes before sending again.")
        return
    update_cooldown(user_id)

    username = f"@{user.username}" if user.username else "N/A"
    msg_to_admin = (
        f"📩 New user reply:\n\n"
        f"🆔 Account ID: {user_id}\n"
        f"Username: {username}\n\n"
        f"📞 Number: `{text}`"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg_to_admin, parse_mode="Markdown")
    await update.message.reply_text("✅ Your reply has been sent to admin!")

async def check_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    try:
        member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", query.from_user.id)
        if member.status in ["member", "administrator", "creator"]:
            data[user_id]["verified2"] = True
            await query.message.reply_text("✅ Verification 2 complete! Welcome!")
            await show_menu(update, query)
        else:
            await query.answer("You are not joined yet.", show_alert=True)
    except Exception:
        await query.answer("You are not joined yet click on Join channel", show_alert=True)

async def show_menu(update: Update, query=None):
    buttons = [
        [InlineKeyboardButton("Menu 1", callback_data="menu1")],
        [InlineKeyboardButton("Menu 2", callback_data="menu2")]
    ]
    text = "🎯 Verification complete! You can now use the bot."
    if query:
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# ===== MAIN =====
async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_joined, pattern="check_joined"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot is running... Press CTRL+C to stop.")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())


