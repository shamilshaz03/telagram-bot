import os
from pymongo import MongoClient
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import logging

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Retrieve environment variables
MONGODB_URI = os.getenv('MONGODB_URI')
DATABASE_NAME = os.getenv('DATABASE_NAME')
CHANNEL_ID = os.getenv('CHANNEL_ID')
ADMIN_ID = int(os.getenv('ADMIN_ID'))
TOTAL_STORAGE_MB = float(os.getenv('TOTAL_STORAGE_MB'))
used_storage = 15.23  # Example, replace with actual calculation if needed
free_storage = TOTAL_STORAGE_MB - used_storage

# MongoDB setup
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
users_collection = db['users']

# List of image URLs
image_urls = [
    'https://example.com/img1.jpg',
    'https://example.com/img2.jpg',
    'https://example.com/img3.jpg',
    'https://example.com/newimg1.jpg',
    'https://example.com/newimg2.jpg'
]

current_page = {}

def add_user(user_id, username):
    """Add or update user data in MongoDB."""
    users_collection.update_one(
        {'user_id': user_id},
        {'$set': {'username': username}},
        upsert=True
    )

def get_user_count():
    """Get the total count of users from MongoDB."""
    return users_collection.count_documents({})

def get_chat_count():
    """Example: Get total chats count."""
    return 950  # Example number of chats

def show_statistics(update, context):
    if update.message.chat_id == ADMIN_ID:
        user_count = get_user_count()
        chat_count = get_chat_count()
        message = (
            f"★ Total Users: {user_count}\n"
            f"★ Total Chats: {chat_count}\n"
            f"★ Used Storage: {used_storage:.2f} MB\n"
            f"★ Free Storage: {free_storage:.2f} MB"
        )
        update.message.reply_text(message)
    else:
        update.message.reply_text("You are not authorized to use this command.")

def show_image(update, context):
    user_id = update.message.chat_id if update.message else update.callback_query.message.chat_id
    page = current_page.get(user_id, 0)
    image_url = image_urls[page]
    keyboard = [
        [InlineKeyboardButton("Previous", callback_data='prev')],
        [InlineKeyboardButton("Next", callback_data='next')],
        [InlineKeyboardButton("Skip Tutorial", callback_data='skip')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_photo(
        chat_id=user_id,
        photo=image_url,
        reply_markup=reply_markup
    )

def button(update, context):
    query = update.callback_query
    user_id = query.message.chat_id
    page = current_page.get(user_id, 0)
    if query.data == 'next':
        if page < len(image_urls) - 1:
            current_page[user_id] += 1
    elif query.data == 'prev':
        if page > 0:
            current_page[user_id] -= 1
    elif query.data == 'skip':
        query.message.reply_text("Tutorial skipped!")
        return
    query.answer()
    show_image(update, context)

def start(update, context):
    user_id = update.message.chat_id
    if users_collection.count_documents({'user_id': user_id}) == 0:
        add_user(user_id, update.message.chat.username)
    notify_channel(f"Bot started. User {user_id} has started the tutorial.")
    current_page[user_id] = 0
    show_image(update, context)

def broadcast(update, context):
    if update.message.chat_id == ADMIN_ID:
        message = ' '.join(context.args)
        broadcast_message(message)
    else:
        update.message.reply_text("You are not authorized to use this command.")

def broadcast_message(message):
    for user in users_collection.find():
        try:
            context.bot.send_message(chat_id=user['user_id'], text=message)
        except Exception as e:
            logging.error(f"Failed to send message to {user['user_id']}: {e}")

def notify_channel(message):
    context.bot.send_message(chat_id=CHANNEL_ID, text=message)

def stop(update, context):
    notify_channel("Bot stopped.")
    updater.stop()

def main():
    global updater
    updater = Updater(os.getenv('TELEGRAM_BOT_TOKEN'))
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CommandHandler('broadcast', broadcast))
    dispatcher.add_handler(CommandHandler('statistics', show_statistics))  # Command for stats

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
