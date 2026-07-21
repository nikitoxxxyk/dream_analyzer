
#!/bin/bash

# Полный путь к Python из venv

PYTHON_PATH="/home/c/cs951513/dream_analyzer/venv/bin/python"

BOT_PATH="/home/c/cs951513/dream_analyzer/bot.py"

LOG_PATH="/home/c/cs951513/dream_analyzer/bot_cron.log"



echo "=== $(date) ===" >> $LOG_PATH



# Проверяем не запущен ли уже бот

if ps aux | grep "python bot.py" | grep -v grep > /dev/null; then

    echo "Bot is already running" >> $LOG_PATH

    exit 0

fi



# Запускаем бота

cd /home/c/cs951513/dream_analyzer

$PYTHON_PATH $BOT_PATH >> $LOG_PATH 2>&1 &



echo "Bot started with PID $!" >> $LOG_PATH

