#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
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

# ==================== HEALTHCHECK SERVER ====================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'🐺 WagerWolf is hunting!')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress healthcheck logs
        return

def run_healthcheck_server():
    """Run a simple HTTP server for Railway healthchecks"""
    try:
        port = int(os.environ.get('PORT', 8080))
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        logger.info(f"🏥 Healthcheck server running on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Healthcheck server error: {e}")

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
        f"""
🐺 *The Wolf is hunting...* 🔍

Your token: {os.environ.get('BOT_TOKEN', 'Not set')[:10]}...

Searching for the best crypto odds!

⚠️ This is a test version. Full features coming soon!
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
        # Start healthcheck server in background thread
        health_thread = threading.Thread(target=run_healthcheck_server, daemon=True)
        health_thread.start()
        logger.info("🏥 Healthcheck server started")
        
        # Get token
        token = os.getenv('BOT_TOKEN')
        if not token:
            logger.error("❌ BOT_TOKEN not set!")
            sys.exit(1)
        
        logger.info("🐺 WagerWolf is starting...")
        
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
