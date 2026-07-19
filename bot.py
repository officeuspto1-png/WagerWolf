#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ==================== LOGGING ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ==================== COMMAND HANDLERS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    user = update.effective_user
    await update.message.reply_text(
        f"🐺 Welcome {user.first_name}! WagerWolf is hunting!",
        parse_mode='Markdown'
    )

async def hunt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hunt command"""
    await update.message.reply_text("🐺 The wolf is hunting for crypto odds!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    await update.message.reply_text(
        "🐺 Commands: /start, /hunt, /help",
        parse_mode='Markdown'
    )

# ==================== MAIN FUNCTION ====================

def main():
    """Start the bot"""
    try:
        token = os.getenv('BOT_TOKEN')
        if not token:
            logger.error("BOT_TOKEN not set!")
            sys.exit(1)
        
        logger.info("🐺 WagerWolf is starting...")
        
        # Create application
        application = Application.builder().token(token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("hunt", hunt_command))
        application.add_handler(CommandHandler("help", help_command))
        
        # Start the bot
        logger.info("✅ WagerWolf is running!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
