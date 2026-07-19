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

*COMMANDS:*
/hunt - Start hunting for odds
/odds <league> - Get crypto odds
/arbitrage - Find arbitrage opportunities
/sniper - Set up sniper alerts
/wallet - Connect your wallet
/premium - Become an Alpha Wolf
/help - Wolf's guidance

🐺 *WARNING:* Only the bold hunt the crypto market!
"""
    
    keyboard = [
        [
            InlineKeyboardButton("🐺 Start Hunt", callback_data="hunt"),
            InlineKeyboardButton("💰 Arbitrage", callback_data="arbitrage")
        ],
        [
            InlineKeyboardButton("🎯 Sniper", callback_data="sniper"),
            InlineKeyboardButton("📊 Stats", callback_data="stats")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wolf's guidance"""
    help_text = """
🐺 *WAGERWOLF - HUNTER'S GUIDE* 🐺

*Basic Commands:*
/hunt - Start hunting odds
/odds <league> - Get crypto odds
/arbitrage - Find arbitrage opportunities
/sniper - Set sniper alerts
/wallet - Manage your crypto wallet
/premium - Unlock Alpha Wolf features

*Hunting Commands:*
/hunt football - Hunt football odds
/hunt nba - Hunt NBA odds
/hunt crypto - Hunt all crypto odds

*Wallet Commands:*
/wallet connect <address> - Connect wallet
/wallet balance - Check balance
/wallet history - View transactions

*Alpha Wolf Features:*
• Priority alerts
• Exclusive arbitrage
• Premium odds
• Advanced analytics

🐺 *Remember:* The wolf hunts the odds, not the other way!
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def hunt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start hunting odds"""
    try:
        await update.message.reply_text(
            "🐺 *The Wolf is hunting...* 🔍\n"
            "Searching for the best crypto odds!",
            parse_mode='Markdown'
        )
        
        # Get crypto odds
        matches = crypto_api.get_odds_with_crypto()
        
        if not matches:
            await update.message.reply_text(
                "🌙 *No prey found...* \n"
                "The wolf will wait. Try again soon!",
                parse_mode='Markdown'
            )
            return
        
        # Analyze matches
        predictions = []
        for match in matches:
            pred = crypto_api.analyze_crypto_bet(match)
            if pred:
                predictions.append(pred)
        
        if not predictions:
            await update.message.reply_text(
                "🐺 *No high-value targets found.*\n"
                "The wolf moves to the next hunt!",
                parse_mode='Markdown'
            )
            return
        
        # Format response
        response = "🐺 *WOLF'S PREY* 🐺\n\n"
        for i, pred in enumerate(predictions[:3]):
            response += crypto_api.format_crypto_prediction(pred)
            if i < len(predictions) - 1:
                response += "\n" + "🌙" * 35 + "\n"
        
        # Add wolf signature
        response += f"\n\n{Utils.create_wolf_signature()}"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Hunt error: {e}")
        await update.message.reply_text(
            "🐺 *The wolf encountered an obstacle.*\n"
            "Regrouping and hunting again!",
            parse_mode='Markdown'
        )

async def odds_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get odds for specific league"""
    try:
        if not context.args:
            await update.message.reply_text(
                "📝 *Usage:* `/odds <league>`\n\n"
                "Examples:\n"
                "`/odds epl` - Premier League\n"
                "`/odds nba` - NBA\n"
                "`/odds champions` - Champions League\n\n"
                "🐺 The wolf adapts to any league!",
                parse_mode='Markdown'
            )
            return
        
        league_query = ' '.join(context.args).lower()
        
        await update.message.reply_text(
            f"🐺 *Hunting {league_query.upper()} odds...*\n"
            "⚡ Tracking the crypto markets!",
            parse_mode='Markdown'
        )
        
        # Fetch and analyze odds
        matches = crypto_api.get_odds_with_crypto()
        
        if not matches:
            await update.message.reply_text("🌙 No matches found.")
            return
        
        # Filter matches
        league_matches = [m for m in matches if league_query in m.get('sport_key', '').lower()]
        
        if not league_matches:
            await update.message.reply_text(
                f"🌙 No matches found for {league_query}.\n"
                "🐺 The wolf hunts elsewhere!",
                parse_mode='Markdown'
            )
            return
        
        predictions = []
        for match in league_matches:
            pred = crypto_api.analyze_crypto_bet(match)
            if pred:
                predictions.append(pred)
        
        if not predictions:
            await update.message.reply_text(
                "🌙 No value bets found.\n"
                "🐺 The wolf waits for better prey!",
                parse_mode='Markdown'
            )
            return
        
        response = f"🐺 *{league_query.upper()} CRYPTO ODDS* 🐺\n\n"
        for i, pred in enumerate(predictions[:3]):
            response += crypto_api.format_crypto_prediction(pred)
            if i < len(predictions) - 1:
                response += "\n" + "🌙" * 35 + "\n"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Odds error: {e}")
        await update.message.reply_text("🐺 Error hunting odds. Try again!")

async def arbitrage_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Find arbitrage opportunities"""
    try:
        await update.message.reply_text(
            "🔄 *The Wolf smells arbitrage!*\n"
            "Scanning for risk-free profits...",
            parse_mode='Markdown'
        )
        
        # Get matches
        matches = crypto_api.get_odds_with_crypto()
        
        if not matches:
            await update.message.reply_text("🌙 No matches to analyze.")
            return
        
        # Find arbitrage opportunities
        opportunities = arbitrage.find_arbitrage(matches)
        
        if not opportunities:
            await update.message.reply_text(
                "🌙 *No arbitrage opportunities found.*\n"
                "🐺 The wolf continues the hunt!",
                parse_mode='Markdown'
            )
            return
        
        # Format response
        response = "🔄 *ARBITRAGE OPPORTUNITIES* 🔄\n\n"
        for opp in opportunities[:3]:
            response += arbitrage.format_arbitrage_message(opp)
            response += "\n" + "⚡" * 35 + "\n"
        
        response += f"\n{Utils.create_wolf_signature()}"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Arbitrage error: {e}")
        await update.message.reply_text("🐺 Error finding arbitrage. Try again!")

async def sniper_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set up sniper alerts"""
    alert_message = """
🎯 *SNIPER MODE ACTIVATED* 🎯

🐺 The wolf is locked on target!

*Sniper Features:*
• 🎯 Odds movement alerts (>5%)
• ⚡ Real-time notifications
• 🔥 High-value opportunities
• 🌙 Premium hunters get priority

*How it works:*
1. I track all odds movements
2. Alert when significant changes occur
3. You strike when the time is right

*Set Alert:*
`/sniper set <match> <target_odds>`

*Examples:*
`/sniper set "Man City vs Arsenal" 2.5`
`/sniper set NBA 1.8`

⚡ *The wolf never misses!*
"""
    await update.message.reply_text(alert_message, parse_mode='Markdown')

async def wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manage crypto wallet"""
    try:
        if not context.args:
            await update.message.reply_text(
                "💳 *Wallet Management*\n\n"
                "Commands:\n"
                "`/wallet connect <address>` - Connect wallet\n"
                "`/wallet balance` - Check balance\n"
                "`/wallet history` - View transactions\n\n"
                "🐺 Secure your crypto with the wolf!",
                parse_mode='Markdown'
            )
            return
        
        action = context.args[0].lower()
        
        if action == 'connect':
            if len(context.args) < 2:
                await update.message.reply_text(
                    "📝 Usage: `/wallet connect <address>`\n"
                    "🐺 Connect your crypto wallet!",
                    parse_mode='Markdown'
                )
                return
            
            address = context.args[1]
            crypto = 'ETH'  # Default
            
            # Try to detect crypto type
            if address.startswith('0x'):
                crypto = 'ETH'
            elif address.startswith('1') or address.startswith('3'):
                crypto = 'BTC'
            
            if Utils.is_valid_crypto_address(address, crypto):
                user = update.effective_user
                db.update_wallet(user.id, address, crypto)
                
                await update.message.reply_text(
                    f"✅ *Wallet Connected!*\n\n"
                    f"📍 Address: `{address}`\n"
                    f"💎 Crypto: {crypto}\n"
                    f"🐺 Your wallet is now guarded by the wolf!",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    "❌ *Invalid wallet address*\n"
                    f"Please check your {crypto} address.",
                    parse_mode='Markdown'
                )
        
        elif action == 'balance':
            await update.message.reply_text(
                "💎 *Wallet Balance*\n\n"
                "📍 Connected: Checking...\n"
                "🐺 The wolf is guarding your crypto!\n\n"
                "(Wallet tracking coming soon!)",
                parse_mode='Markdown'
            )
        
        elif action == 'history':
            await update.message.reply_text(
                "📊 *Transaction History*\n\n"
                "🐺 Tracking your wolf pack's movements!\n\n"
                "(History coming soon!)",
                parse_mode='Markdown'
            )
        
        else:
            await update.message.reply_text(
                f"❌ Unknown action: {action}\n"
                "Use: connect, balance, or history",
                parse_mode='Markdown'
            )
        
    except Exception as e:
        logger.error(f"Wallet error: {e}")
        await update.message.reply_text("🐺 Error managing wallet. Try again!")

async def premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Premium features"""
    premium_message = f"""
🐺 *ALPHA WOLF STATUS* 🐺

Unlock the full power of WagerWolf!

*PREMIUM FEATURES:*
🔥 Priority arbitrage alerts
🌙 Exclusive odds data
⚡ Real-time sniper notifications
💀 Advanced analytics
🎯 Premium support

*PRICE:* {Config.PREMIUM_PRICE}

*How to Upgrade:*
1. Send payment to: (Coming soon)
2. Confirm transaction
3. Become an Alpha Wolf!

*Benefits:*
• 5x faster alerts
• Exclusive opportunities
• Higher profit margins
• VIP hunting ground

🐺 *Join the elite wolf pack!*
"""
    await update.message.reply_text(premium_message, parse_mode='Markdown')

# ==================== CALLBACK HANDLERS ====================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "hunt":
        await hunt_command(update, context)
    elif data == "arbitrage":
        await arbitrage_command(update, context)
    elif data == "sniper":
        await sniper_command(update, context)
    elif data == "stats":
        await query.edit_message_text(
            "📊 *WOLF STATS* 📊\n\n"
            "🐺 Hunts completed: Tracking...\n"
            "💰 Profits found: Calculating...\n"
            "🎯 Targets acquired: Active\n"
            "🌙 The wolf is always hunting!\n\n"
            "Check `/hunt` for latest prey!",
            parse_mode='Markdown'
        )

# ==================== MESSAGE HANDLER ====================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle crypto-related messages"""
    text = update.message.text
    
    # Check for crypto mentions
    crypto = Utils.extract_crypto_from_text(text)
    if crypto:
        await update.message.reply_text(
            f"🐺 *The wolf tracks {crypto}!*\n"
            f"Use `/hunt` to find the best {crypto} odds!",
            parse_mode='Markdown'
        )
        return
    
    # Default response
    response = """
🐺 *WAGERWOLF*

The wolf doesn't understand that command.

*Try:*
`/hunt` - Start hunting
`/arbitrage` - Find risk-free profits
`/sniper` - Set alerts
`/help` - Wolf's guidance

🐺 *The hunt continues!*
"""
    await update.message.reply_text(response, parse_mode='Markdown')

# ==================== MAIN FUNCTION ====================

def main():
    """Start the wolf"""
    try:
        # Start healthcheck
        health_thread = threading.Thread(target=run_healthcheck_server, daemon=True)
        health_thread.start()
        
        # Start sniper
        sniper.start_sniping()
        
        logger.info("🐺 WagerWolf is hunting!")
        
        # Create application
        application = Application.builder().token(Config.BOT_TOKEN).build()
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("hunt", hunt_command))
        application.add_handler(CommandHandler("odds", odds_command))
        application.add_handler(CommandHandler("arbitrage", arbitrage_command))
        application.add_handler(CommandHandler("sniper", sniper_command))
        application.add_handler(CommandHandler("wallet", wallet_command))
        application.add_handler(CommandHandler("premium", premium_command))
        
        # Add callback handler
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # Add message handler
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Start bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    main()
