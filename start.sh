#!/bin/bash
if [ -z "$UPSTREAM_REPO" ]
then
  echo "Cloning main repository..."
  git clone https://github.com/shamilshaz03/telagram-bot.git /app
else
  echo "Cloning custom repository from $UPSTREAM_REPO..."
  git clone $UPSTREAM_REPO /app
fi
cd /app
pip3 install -r requirements.txt
echo "Starting bot..."
python3 bot.py
