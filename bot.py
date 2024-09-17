from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import config

# List of images for the tutorial
images = ['images/img1.jpg', 'images/img2.jpg', 'images/img3.jpg']
current_page = {}

# Define the start function
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id
    current_page[user_id] = 0  # Track the current image per user
    show_image(update, context)

def show_image(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id
    page = current_page.get(user_id, 0)
    
    keyboard = [
        [InlineKeyboardButton("Previous", callback_data='prev')],
        [InlineKeyboardButton("Next", callback_data='next')],
        [InlineKeyboardButton("Skip Tutorial", callback_data='skip')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send image with inline buttons
    context.bot.send_photo(
        chat_id=user_id,
        photo=open(images[page], 'rb'),
        reply_markup=reply_markup
    )

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.message.chat_id
    page = current_page.get(user_id, 0)

    if query.data == 'next':
        if page < len(images) - 1:
            current_page[user_id] += 1
    elif query.data == 'prev':
        if page > 0:
            current_page[user_id] -= 1
    elif query.data == 'skip':
        show_payment_options(update, context)
        return
    
    query.answer()
    show_image(update, context)

def show_payment_options(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Google Pay", url=config.GPAY_URL)],
        [InlineKeyboardButton("Paytm", url=config.PAYTM_URL)],
        [InlineKeyboardButton("PhonePe", url=config.PHONEPE_URL)],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.callback_query.message.reply_text(
        'Select a payment method:', reply_markup=reply_markup
    )

def main() -> None:
    updater = Updater(config.TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
