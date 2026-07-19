import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Aggressive crypto betting configuration"""
    
    # Telegram Bot
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not found")
    
    # Crypto APIs
    ODDS_API_KEY = os.getenv('ODDS_API_KEY')
    STAKE_API_KEY = os.getenv('STAKE_API_KEY')
    BET365_API_KEY = os.getenv('BET365_API_KEY')
    
    # Crypto Price APIs
    COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY')
    CRYPTOCOMPARE_API_KEY = os.getenv('CRYPTOCOMPARE_API_KEY')
    
    # Supported Cryptocurrencies
    SUPPORTED_CRYPTO = os.getenv('SUPPORTED_CRYPTO', 'BTC,ETH,SOL,MATIC,USDT').split(',')
    
    # Crypto Emojis
    CRYPTO_EMOJIS = {
        'BTC': '₿',
        'ETH': '⟠',
        'SOL': '◎',
        'MATIC': '◆',
        'USDT': '₮',
        'USDC': '💵'
    }
    
    # Crypto Sportsbooks
    CRYPTO_BOOKMAKERS = [
        'stake',
        'rollbit',
        'bcgame',
        'bitstarz',
        'cloudbet',
        'fortunejack'
    ]
    
    # Odds Aggregation
    DEFAULT_CURRENCY = os.getenv('DEFAULT_CURRENCY', 'USDT')
    ARBITRAGE_THRESHOLD = float(os.getenv('ARBITRAGE_THRESHOLD', '2.0'))
    SNIPER_INTERVAL = int(os.getenv('SNIPER_INTERVAL', '60'))
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///wagerwolf.db')
    
    # Premium Features
    PREMIUM_ENABLED = os.getenv('PREMIUM_ENABLED', 'true').lower() == 'true'
    PREMIUM_PRICE = os.getenv('PREMIUM_PRICE', '0.001 ETH')
    
    # Wolf Branding
    WOLF_EMOJIS = ['🐺', '🌙', '🔥', '⚡', '💀']
    WOLF_THEME = {
        'primary': '🔥',
        'secondary': '🌙',
        'accent': '⚡',
        'danger': '💀',
        'success': '🐺'
    }
    
    # League Names (crypto focused)
    LEAGUE_NAMES = {
        'england_premier_league': '🏴󠁧󠁢󠁥󠁮󠁧󠁿 EPL',
        'spain_la_liga': '🇪🇸 La Liga',
        'italy_serie_a': '🇮🇹 Serie A',
        'germany_bundesliga': '🇩🇪 Bundesliga',
        'france_ligue_one': '🇫🇷 Ligue 1',
        'usa_nba': '🏀 NBA',
        'mlb': '⚾ MLB',
        'atp': '🎾 ATP'
    }
    
    # Bet types with crypto flavor
    BET_TYPES = {
        'moneyline': '💀 Moneyline',
        'spread': '🐺 Spread',
        'total': '🔥 Total',
        'parlay': '⚡ Parlay',
        'arbitrage': '🔄 Arbitrage'
    }
