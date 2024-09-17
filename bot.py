from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import config
import os

# Define the path to the images folder
IMAGE_FOLDER = 'images/'

# List of image files for the tutorial
images = ['img1.jpg', 'img2.jpg', 'img3.jpg']
current_page = {}

# Function to send an image based on user interaction
def show_image(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id if update.message else update.callback_query.message.chat_id
    page = current_page.get(user_id, 0)
    
    # Construct the full path to the image
    image_path = os.path.join(IMAGE_FOLDER, images[page])
    
    # Create navigation buttons
    keyboard = [
        [InlineKeyboardButton("Previous", callback_data='prev')],
        [InlineKeyboardButton("Next", callback_data='next')],
        [InlineKeyboardButton("Skip Tutorial", callback_data='skip')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the image with inline buttons
    if os.path.exists(image_path):
        context.bot.send_photo(
            chat_id=user_id,
            photo=open(image_path, 'rb'),  # Open the image file
            reply_markup=reply_markup
        )
    else:
        context.bot.send_message(chat_id=user_id, text="Image not found!")

# Function to handle button presses
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.message.chat_id
    page = current_page.get(user_id, 0)

    # Handle next and previous buttons
    if query.data == 'next':
        if page < len(images) - 1:
            current_page[user_id] += 1  # Move to the next image
    elif query.data == 'prev':
        if page > 0:
            current_page[user_id] -= 1  # Move to the previous image
    elif query.data == 'skip':
        show_payment_options(update, context)  # Show payment options after skipping
        return
    
    query.answer()  # Acknowledge the button press
    show_image(update, context)  # Show the corresponding image based on the button pressed

# Function to show payment options after the tutorial
def show_payment_options(update: Update, context: CallbackContext) -> None:
    # Set up payment option buttons
    keyboard = [
        [InlineKeyboardButton("Google Pay", url=config.GPAY_URL)],
        [InlineKeyboardButton("Paytm", url=config.PAYTM_URL)],
        [InlineKeyboardButton("PhonePe", url=config.PHONEPE_URL)],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the payment options
    update.callback_query.message.reply_text(
        'Select a payment method:', reply_markup=reply_markup
    )

# Start command to initialize the tutorial
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id
    current_page[user_id] = 0  # Initialize tutorial for this user
    show_image(update, context)  # Show the first image

# Main function to start the bot
def main() -> None:
    updater = Updater(config.TOKEN)
    dispatcher = updater.dispatcher

    # Add command handler to start the bot
    dispatcher.add_handler(CommandHandler('start', start))
    
    # Add callback query handler to process button clicks
    dispatcher.add_handler(CallbackQueryHandler(button))

    # Start polling for updates
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
