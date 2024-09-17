import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler
from pymongo import MongoClient

# Retrieve environment variables
BOT_TOKEN = os.getenv('TOKEN')
MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME')
ADMIN_ID = int(os.getenv('ADMIN_ID'))  # Admin ID for managing admin-only functionality

# Initialize MongoDB client
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB_NAME]

# Example image URLs
images = [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg",
    "https://example.com/image3.jpg"
]

# Define a function to handle /start command
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Next", callback_data='next')],
        [InlineKeyboardButton("Previous", callback_data='previous')],
        [InlineKeyboardButton("Skip Tutorial", callback_data='skip')],
        [InlineKeyboardButton("Payment Options", callback_data='payment')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Welcome to the bot! Choose an option:', reply_markup=reply_markup)

# Define a function to handle button presses
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data

    # Check the callback data and respond accordingly
    if data == 'next':
        await show_image(update, query, 1)
    elif data == 'previous':
        await show_image(update, query, -1)
    elif data == 'skip':
        await query.edit_message_text(text="Tutorial skipped!")
        await show_payment_options(update, query)
    elif data == 'payment':
        await show_payment_options(update, query)

async def show_image(update: Update, query, step) -> None:
    # Retrieve the current image index
    current_index = int(query.message.caption.split()[1]) if query.message.caption else 0
    new_index = (current_index + step) % len(images)
    media = InputMediaPhoto(images[new_index], caption=f"Image {new_index + 1}")
    
    keyboard = [
        [InlineKeyboardButton("Next", callback_data='next')],
        [InlineKeyboardButton("Previous", callback_data='previous')],
        [InlineKeyboardButton("Skip Tutorial", callback_data='skip')],
        [InlineKeyboardButton("Payment Options", callback_data='payment')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_media(media=media)
    await query.edit_message_reply_markup(reply_markup=reply_markup)

async def show_payment_options(update: Update, query) -> None:
    payment_keyboard = [
        [InlineKeyboardButton("Google Pay", url="https://example.com/googlepay")],
        [InlineKeyboardButton("Paytm", url="https://example.com/paytm")],
        [InlineKeyboardButton("PhonePe", url="https://example.com/phonepe")]
    ]
    reply_markup = InlineKeyboardMarkup(payment_keyboard)
    await query.edit_message_text(text="Choose a payment option:", reply_markup=reply_markup)

# Admin command to display user count
async def admin(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id == ADMIN_ID:
        user_count = db.users.count_documents({})
        await update.message.reply_text(f"Total users: {user_count}")
    else:
        await update.message.reply_text("You are not authorized to use this command.")

def main():
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers for /start command and button presses
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler('admin', admin))

    # Run the bot until you send a signal to stop
    application.run_polling()

if __name__ == '__main__':
    main()
