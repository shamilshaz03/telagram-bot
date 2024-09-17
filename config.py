import os

# Telegram Bot Token from @BotFather
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_API_TOKEN')

# Admin configuration
ADMIN_ID = int(os.getenv('ADMIN_ID', 'YOUR_TELEGRAM_USER_ID'))

# Payment links
GPAY_URL = os.getenv('GPAY_URL', 'https://gpay.payment.link')
PAYTM_URL = os.getenv('PAYTM_URL', 'https://paytm.payment.link')
PHONEPE_URL = os.getenv('PHONEPE_URL', 'https://phonepe.payment.link')

# MongoDB configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'telegram_bot')

# Channel configuration
CHANNEL_ID = os.getenv('CHANNEL_ID', '@your_channel')

# Storage configuration
TOTAL_STORAGE_MB = float(os.getenv('TOTAL_STORAGE_MB', '512'))

# Default image URLs (replace with actual URLs)
DEFAULT_IMAGE_URLS = [
    'https://example.com/img1.jpg',
    'https://example.com/img2.jpg',
    'https://example.com/img3.jpg'
]
