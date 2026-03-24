import os
import asyncio
import json
from flask import Flask
import threading

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

TOKEN = os.getenv("TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

# 🌐 Flask keep alive
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host='0.0.0.0', port=port)

# 📦 Data files
USERS_FILE = "users.json"

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return list(set(json.load(f)))
    except:
        return []

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

# 📩 mapping (reply system)
message_map = {}

# 📩 Forward ALL messages
async def forward_to_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    save_user(user.id)

    # typing effect
    await context.bot.send_chat_action(chat_id=OWNER_ID, action="typing")

    msg = update.message

    if msg.text:
        sent = await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"📩 {user.first_name}:\n{msg.text}"
        )

    elif msg.photo:
        sent = await context.bot.send_photo(
            chat_id=OWNER_ID,
            photo=msg.photo[-1].file_id,
            caption=f"📸 {user.first_name}"
        )

    elif msg.video:
        sent = await context.bot.send_video(
            chat_id=OWNER_ID,
            video=msg.video.file_id,
            caption=f"🎥 {user.first_name}"
        )

    elif msg.document:
        sent = await context.bot.send_document(
            chat_id=OWNER_ID,
            document=msg.document.file_id,
            caption=f"📄 {user.first_name}"
        )

    else:
        return

    message_map[sent.message_id] = user.id

    # 🧾 save chat
    with open(f"chat_{user.id}.txt", "a") as f:
        if msg.text:
            f.write(msg.text + "\n")

# 🔁 Reply back to user
async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        replied_id = update.message.reply_to_message.message_id

        if replied_id in message_map:
            user_id = message_map[replied_id]

            await context.bot.send_chat_action(chat_id=user_id, action="typing")

            if update.message.text:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=update.message.text
                )

# 📢 Broadcast
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        return

    users = load_users()

    if not context.args:
        await update.message.reply_text("Use: /broadcast message")
        return

    msg = " ".join(context.args)

    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=msg)
        except:
            pass

    await update.message.reply_text(f"✅ Sent to {len(users)} users")

# 📊 Stats
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        return

    users = load_users()
    await update.message.reply_text(f"👥 Total Users: {len(users)}")

# 🤖 Auto reply (basic AI feel)
async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "hello" in text:
        await update.message.reply_text("Hello bhai 😎")
    elif "help" in text:
        await update.message.reply_text("Kya help chahiye bolo 💬")

# 🚀 MAIN
async def main():
    threading.Thread(target=run_flask, daemon=True).start()

    app = ApplicationBuilder().token(TOKEN).build()

    # user messages
    app.add_handler(MessageHandler(filters.ALL & ~filters.User(OWNER_ID), forward_to_owner))

    # owner reply
    app.add_handler(MessageHandler(filters.TEXT & filters.User(OWNER_ID), reply_to_user))

    # commands
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("stats", stats))

    # auto reply
    app.add_handler(MessageHandler(filters.TEXT & ~filters.User(OWNER_ID), auto_reply))

    print("🤖 Bot started...")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    # bot ko alive rakho
    while True:
        await asyncio.sleep(1000)

# RUN
asyncio.run(main())
