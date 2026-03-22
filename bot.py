import os
import asyncio
from flask import Flask
import threading

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

# 🌐 Flask
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host='0.0.0.0', port=port)

# 📩 mapping
message_map = {}

async def forward_to_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    if update.message.text:
        sent_msg = await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"📩 {user.first_name}:\n{update.message.text}"
        )
        message_map[sent_msg.message_id] = user.id

async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        replied_msg_id = update.message.reply_to_message.message_id

        if replied_msg_id in message_map:
            user_id = message_map[replied_msg_id]

            if update.message.text:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=update.message.text
                )

# 🚀 MAIN ASYNC FIX
async def main():
    # Flask thread
    threading.Thread(target=run_flask, daemon=True).start()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.User(OWNER_ID), forward_to_owner))
    app.add_handler(MessageHandler(filters.TEXT & filters.User(OWNER_ID), reply_to_user))

    print("🤖 Bot started...")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    # bot ko alive rakho
    while True:
        await asyncio.sleep(1000)

# RUN
asyncio.run(main())
