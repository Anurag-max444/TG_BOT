import os
from flask import Flask
import threading

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# 🔑 TOKEN & OWNER ID
TOKEN = os.getenv("TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

# 🌐 Flask server (Render ke liye)
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app_flask.run(host='0.0.0.0', port=10000)

# 📩 message mapping
message_map = {}

# user → owner
async def forward_to_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    sent_msg = await context.bot.send_message(
        chat_id=OWNER_ID,
        text=f"📩 {user.first_name}:\n{update.message.text}"
    )
    
    message_map[sent_msg.message_id] = user.id

# owner → user
async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        replied_msg_id = update.message.reply_to_message.message_id
        
        if replied_msg_id in message_map:
            user_id = message_map[replied_msg_id]
            
            await context.bot.send_message(
                chat_id=user_id,
                text=update.message.text
            )

# 🚀 MAIN START
def main():
    # Flask ko alag thread me chala
    threading.Thread(target=run_flask).start()

    # Bot start
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.User(OWNER_ID), forward_to_owner))
    app.add_handler(MessageHandler(filters.TEXT & filters.User(OWNER_ID), reply_to_user))

    print("🤖 Bot started...")
    app.run_polling()

# RUN
if __name__ == "__main__":
    main()
