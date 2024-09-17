import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler
import pymongo
import config

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MongoDB client
client = pymongo.MongoClient(config.MONGODB_URI)
db = client[config.MONGODB_DB_NAME]  # Ensure MONGODB_DB_NAME exists in config.py
users_collection = db['users']

# Define a function to handle /start command
async def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_data = {
        'user_id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name
    }
    users_collection.update_one({'user_id': user.id}, {'$set': user_data}, upsert=True)
    
    keyboard = [
        [InlineKeyboardButton("Next", callback_data='next')],
        [InlineKeyboardButton("Previous", callback_data='previous')],
        [InlineKeyboardButton("Skip Tutorial", callback_data='skip')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text('Welcome to the bot tutorial!', reply_markup=reply_markup)

# Handle callback queries
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data
    
    if data == 'next':
        # Display the next image (update with your own logic)
        image_url = "https://example.com/next_image.jpg"
        await query.message.reply_photo(photo=image_url)
    elif data == 'previous':
        # Display the previous image (update with your own logic)
        image_url = "https://example.com/previous_image.jpg"
        await query.message.reply_photo(photo=image_url)
    elif data == 'skip':
        # Display payment options
        keyboard = [
            [InlineKeyboardButton("Google Pay", url=config.GPAY_URL)],
            [InlineKeyboardButton("Paytm", url=config.PAYTM_URL)],
            [InlineKeyboardButton("PhonePe", url=config.PHONEPE_URL)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text('Select a payment method:', reply_markup=reply_markup)
    
    await query.answer()

# Handle /broadcast command (admin only)
async def broadcast(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != int(config.ADMIN_ID):
        await update.message.reply_text("You are not authorized to use this command.")
        return
    
    message = ' '.join(context.args)
    if not message:
        await update.message.reply_text("Please provide a message to broadcast.")
        return
    
    users = users_collection.find()
    for user in users:
        try:
            await context.bot.send_message(chat_id=user['user_id'], text=message)
        except Exception as e:
            logger.error(f"Failed to send message to user {user['user_id']}: {e}")
    
    await update.message.reply_text("Broadcast message sent.")

# Handle /usercount command (admin only)
async def user_count(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != int(config.ADMIN_ID):
        await update.message.reply_text("You are not authorized to use this command.")
        return
    
    total_users = users_collection.count_documents({})
    await update.message.reply_text(f"★ Total Users: {total_users}")

def main():
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(config.TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('broadcast', broadcast))
    application.add_handler(CommandHandler('usercount', user_count))
    application.add_handler(CallbackQueryHandler(button))

    # Run the bot until you send a signal to stop
    application.run_polling()

if __name__ == '__main__':
    main()
