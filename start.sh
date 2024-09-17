#!/bin/bash

# Check if UPSTREAM_REPO is set, otherwise clone the main repository
if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone https://github.com/shamilshaz03/telagram-bot.git /telegram-bot
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /telegram-bot
fi

# Change directory to the bot folder
cd /telegram-bot

# Install dependencies from requirements.txt
pip3 install -U -r requirements.txt

# Start the bot
echo "Starting Telegram Bot..."
python3 bot.py
