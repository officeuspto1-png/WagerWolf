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
        f"""
🐺 *WELCOME TO WAGERWOLF* 🐺

*The Wolf has arrived, {user.first_name}!*

🔥 I hunt the best crypto odds across the blockchain

*COMMANDS:*
/hunt - Start hunting for odds
/help - Wolf's guidance

🐺 *WARNING:* Only the bold hunt the crypto market!
""",
        parse_mode='Markdown'
    )

async def hunt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hunt command"""
    await update.message.reply_text(
        """
🐺 *The Wolf is hunting...* 🔍

Searching for the best crypto odds!

⚠️ Full features coming soon! Stay tuned.
""",
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    await update.message.reply_text(
        """
🐺 *WAGERWOLF - HUNTER'S GUIDE* 🐺

*Commands:*
/start - Welcome message
/hunt - Start hunting odds
/help - Show this help

🐺 *Remember:* The wolf hunts the odds!
""",
        parse_mode='Markdown'
    )

# ==================== MAIN FUNCTION ====================

def main():
    """Start the bot"""
    try:
        # Get token
        token = os.getenv('BOT_TOKEN')
        if not token:
            logger.error("❌ BOT_TOKEN not set!")
            sys.exit(1)
        
        logger.info("🐺 WagerWolf is starting...")
        logger.info(f"📡 BOT_TOKEN: {token[:10]}...")
        
        # Create application
        application = Application.builder().token(token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("hunt", hunt_command))
        application.add_handler(CommandHandler("help", help_command))
        
        # Start the bot
        logger.info("✅ WagerWolf is running and hunting!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
