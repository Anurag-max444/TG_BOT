!pip install python-telegram-bot nest_asyncio

import nest_asyncio
nest_asyncio.apply()

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8343738974:AAG-_FNN6DVQLnCtKOXRIPpBbzbEDKxXGTA"
OWNER_ID = 6668500692

# store mapping: forwarded message id → user id
message_map = {}

# user → owner
async def forward_to_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    sent_msg = await context.bot.send_message(
        chat_id=OWNER_ID,
        text=f"📩 {user.first_name}:\n{update.message.text}"
    )
    
    # mapping store karo
    message_map[sent_msg.message_id] = user.id


# owner → user (reply system)
async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        replied_msg_id = update.message.reply_to_message.message_id
        
        if replied_msg_id in message_map:
            user_id = message_map[replied_msg_id]
            
            await context.bot.send_message(
                chat_id=user_id,
                text=update.message.text
            )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.User(OWNER_ID), forward_to_owner))
app.add_handler(MessageHandler(filters.TEXT & filters.User(OWNER_ID), reply_to_user))

app.run_polling()