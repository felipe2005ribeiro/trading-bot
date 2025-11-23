#!/bin/bash
# Health check script for Railway
# Returns success if bot is running

if pgrep -f "run_bot.py" > /dev/null; then
    echo "Bot is running"
    exit 0
else
    echo "Bot is not running"
    exit 1
fi
