#!/bin/bash
# AI News Bot Runner Script
# This script is called by cron every day at 8:00 AM

# Set environment
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

# Project directory
PROJECT_DIR="/Users/xing/Downloads/client_demo/ai_news_bot"
VENV_PYTHON="/Users/xing/Downloads/client_demo/venv/bin/python"

# Log file
LOG_FILE="$PROJECT_DIR/cron.log"

# Run the bot
echo "$(date): Starting AI News Bot..." >> "$LOG_FILE"
cd "$PROJECT_DIR"
"$VENV_PYTHON" main.py >> "$LOG_FILE" 2>&1
echo "$(date): AI News Bot finished" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"
