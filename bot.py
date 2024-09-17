from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

# List of image URLs for the tutorial
image_urls = [
    'https://example.com/img1.jpg',  # Replace with actual URL
    'https://example.com/img2.jpg',  # Replace with actual URL
    'https://example.com/img3.jpg'   # Replace with actual URL
]

# Dictionary to keep track of the current page (or image) for each user
current_page = {}

# Function to send an image from a URL
def show_image(update, context):
    user_id = update.message.chat_id if update.message else update.callback_query.message.chat_id
    page = current_page.get(user_id, 0)  # Get the current page (default to 0)

    # Get the URL of the current image
    image_url = image_urls[page]

    # Create navigation buttons
    keyboard = [
        [InlineKeyboardButton("Previous", callback_data='prev')],
        [InlineKeyboardButton("Next", callback_data='next')],
        [InlineKeyboardButton("Skip Tutorial", callback_data='skip')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the image using the URL
    context.bot.send_photo(
        chat_id=user_id,
        photo=image_url,  # Use the URL instead of opening a local file
        reply_markup=reply_markup
    )

# Button handler function
def button(update, context):
    query = update.callback_query
    user_id = query.message.chat_id
    page = current_page.get(user_id, 0)  # Get the current page (image number)

    if query.data == 'next':
        if page < len(image_urls) - 1:  # Check if there's a next image
            current_page[user_id] += 1  # Move to the next image
    elif query.data == 'prev':
        if page > 0:  # Check if there's a previous image
            current_page[user_id] -= 1  # Move to the previous image
    elif query.data == 'skip':
        query.message.reply_text("Tutorial skipped!")  # Handle skip action
        return

    query.answer()  # Acknowledge the button press
    show_image(update, context)  # Show the updated image

# Start command (first image shown)
def start(update, context):
    user_id = update.message.chat_id
    current_page[user_id] = 0  # Start at the first image
    show_image(update, context)  # Display the first image

# Main function
def main():
    # Initialize the bot with your token
    updater = Updater('YOUR_TELEGRAM_BOT_TOKEN')
    dispatcher = updater.dispatcher

    # Add command handler for the /start command
    dispatcher.add_handler(CommandHandler('start', start))
    
    # Add handler for button clicks
    dispatcher.add_handler(CallbackQueryHandler(button))

    # Start polling for updates
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
