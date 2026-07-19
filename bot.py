#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import os
import traceback
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

from config import Config
from crypto_api import CryptoOddsAPI
from arbitrage import ArbitrageDetector
from sniper import OddsSniper
from database import Database
from utils import Utils

# ==================== LOGGING ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('wagerwolf.log')
    ]
)
logger = logging.getLogger(__name__)

# ==================== HEALTHCHECK ====================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'🐺 WagerWolf is hunting!')
        else:
            self.send_response(404)
            self.end_headers()

def run_healthcheck_server():
    try:
        port = int(os.environ.get('PORT', 8080))
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        logger.info(f"🏥 Healthcheck server running on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Healthcheck error: {e}")

# ==================== INITIALIZATION ====================
crypto_api = CryptoOddsAPI()
arbitrage = ArbitrageDetector()
sniper = OddsSniper()
db = Database()

# ==================== ERROR HANDLER ====================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")
    logger.error(traceback.format_exc())
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "🐺 *The wolf senses something went wrong!*\n"
                "Try again later, hunter! 🌙",
                parse_mode='Markdown'
            )
    except:
        pass

# ==================== COMMAND HANDLERS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wolf's welcome"""
    user = update.effective_user
    
    # Register user
    db.add_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name
    )
    
    welcome_message = f"""
🐺 *WELCOME TO WAGERWOLF* 🐺

*The Wolf has arrived, {user.first_name}!*

🔥 I hunt the best crypto odds across the blockchain
🌙 I track every movement in the market
⚡ I strike when opportunity appears

*WHAT I CAN DO:*
• 🐺 *Crypto Odds* - Best odds in USDT, BTC, ETH
• 🔄 *Arbitrage* - Risk-free profit opportunities
• 🎯 *Sniper Alerts* - Odds movement notifications
• 💰 *Value Bets* - High-value crypto picks
• 📊 *Wallet Tracking* - Track your crypto bets

*COMMANDS:
