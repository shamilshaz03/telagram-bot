import os
import logging
from pymongo import MongoClient
from telegram import Update, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Retrieve environment variables
MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME')
TOKEN = os.getenv('TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))

# Check environment variables
if not MONGODB_URI:
    raise ValueError("Missing MongoDB URI")
if not MONGODB_DB_NAME or not isinstance(MONGODB_DB_NAME, str):
    raise ValueError("MONGODB_DB_NAME must be a valid string")
if not TOKEN:
    raise ValueError("Missing Telegram Bot Token")
if not ADMIN_ID:
    raise ValueError("Missing Admin ID")

# Initialize MongoDB client and database
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB_NAME]

# Bot image links
IMAGES = [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg",
    "https://example.com/image3.jpg"
]
current_image_index = 0

# Define handlers

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Next", callback_data='next')],
        [InlineKeyboardButton("Previous", callback_data='prev')],
        [InlineKeyboardButton("Skip Tutorial", callback_data='skip')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_photo(photo=IMAGES[current_image_index], reply_markup=reply_markup)

async def button(update: Update, context: CallbackContext):
    global current_image_index
    query = update.callback_query
    data = query.data

    if data == 'next':
        current_image_index = (current_image_index + 1) % len(IMAGES)
    elif data == 'prev':
        current_image_index = (current_image_index - 1) % len(IMAGES)
    elif data == 'skip':
        await query.edit_message_text(text="Tutorial skipped. Here are the payment options:")
        keyboard = [
            [InlineKeyboardButton("Google Pay", url="https://example.com/googlepay")],
            [InlineKeyboardButton("Paytm", url="https://example.com/paytm")],
            [InlineKeyboardButton("PhonePe", url="https://example.com/phonepe")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Payment Options:", reply_markup=reply_markup)
        return

    await query.edit_message_media(media=InputMediaPhoto(media=IMAGES[current_image_index]))

async def admin_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("User Count", callback_data='user_count')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Admin Options:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("You are not authorized to use this command.")

async def handle_admin_query(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    if data == 'user_count':
        user_count = db['users'].count_documents({})
        await query.answer(text=f"Total users: {user_count}")

# Set up the bot
application = Application.builder().token(TOKEN).build()

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button))
application.add_handler(CommandHandler("admin", admin_command))
application.add_handler(CallbackQueryHandler(handle_admin_query))

# Start the bot
if __name__ == '__main__':
    application.run_polling()
