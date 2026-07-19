import requests
import time
import json
from datetime import datetime, timedelta
from cachetools import cached, TTLCache
from typing import Dict, List, Any
from config import Config

cache = TTLCache(maxsize=200, ttl=30)

class CryptoOddsAPI:
    """Crypto-focused odds aggregator"""
    
    def __init__(self):
        self.api_key = Config.ODDS_API_KEY
        self.base_url = Config.ODDS_API_BASE_URL
        self.session = requests.Session()
        self.crypto_prices = {}
        self.last_price_update = None
    
    def get_crypto_price(self, crypto: str = 'USDT') -> float:
        """Get current crypto price in USD"""
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': crypto.lower(),
                'vs_currencies': 'usd'
            }
            if Config.COINGECKO_API_KEY:
                params['x_cg_pro_api_key'] = Config.COINGECKO_API_KEY
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get(crypto.lower(), {}).get('usd', 0)
        except Exception as e:
            print(f"Error fetching crypto price: {e}")
        return 0
    
    def get_all_crypto_prices(self):
        """Get prices for all supported cryptocurrencies"""
        prices = {}
        for crypto in Config.SUPPORTED_CRYPTO:
            prices[crypto] = self.get_crypto_price(crypto)
            time.sleep(0.1)
        self.crypto_prices = prices
        self.last_price_update = datetime.utcnow()
        return prices
    
    def get_odds_with_crypto(self, sport='soccer', region='eu', markets='h2h'):
        """Fetch odds and convert to crypto values"""
        try:
            url = f"{self.base_url}/sports/{sport}/odds"
            params = {
                'apiKey': self.api_key,
                'region': region,
                'markets': markets,
                'dateFormat': 'iso'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 429:
                time.sleep(5)
                response = self.session.get(url, params=params, timeout=15)
            
            response.raise_for_status()
            matches = response.json()
            
            # Convert to crypto prices
            crypto_prices = self.get_all_crypto_prices()
            
            for match in matches:
                for bookmaker in match.get('bookmakers', []):
                    # Add crypto conversion
                    for market in bookmaker.get('markets', []):
                        for outcome in market.get('outcomes', []):
                            if 'price' in outcome:
                                # Convert to USDT
                                usdt_price = outcome['price']
                                for crypto, usd_price in crypto_prices.items():
                                    if usd_price > 0:
                                        outcome[f'{crypto}_price'] = usdt_price / usd_price
            
            return matches
            
        except Exception as e:
            print(f"Error fetching crypto odds: {e}")
            return []
    
    def analyze_crypto_bet(self, match: Dict) -> Dict:
        """Analyze bet with crypto value consideration"""
        try:
            if not match.get('bookmakers'):
                return None
            
            # Get best odds across crypto bookmakers
            best_odds = {'home': 0, 'draw': 0, 'away': 0}
            best_bookmaker = {'home': '', 'draw': '', 'away': ''}
            
            for bookmaker in match['bookmakers']:
                if bookmaker['key'] not in Config.CRYPTO_BOOKMAKERS:
                    continue
                
                for market in bookmaker.get('markets', []):
                    if market['key'] == 'h2h':
                        outcomes = market.get('outcomes', [])
                        for outcome in outcomes:
                            name = outcome.get('name', '')
                            price = outcome.get('price', 0)
                            
                            # Check crypto prices
                            for crypto in Config.SUPPORTED_CRYPTO:
                                crypto_price = outcome.get(f'{crypto}_price', 0)
                                if crypto_price > 0:
                                    price = crypto_price
                            
                            if name == match.get('home_team', ''):
                                if price > best_odds['home']:
                                    best_odds['home'] = price
                                    best_bookmaker['home'] = bookmaker['key']
                            elif name == match.get('away_team', ''):
                                if price > best_odds['away']:
                                    best_odds['away'] = price
                                    best_bookmaker['away'] = bookmaker['key']
                            elif name == 'Draw':
                                if price > best_odds['draw']:
                                    best_odds['draw'] = price
                                    best_bookmaker['draw'] = bookmaker['key']
            
            # Calculate value
            if best_odds['home'] > 0 and best_odds['away'] > 0:
                total_prob = (1/best_odds['home']) + (1/best_odds['draw']) + (1/best_odds['away'])
                home_prob = (1/best_odds['home']) / total_prob * 100
                draw_prob = (1/best_odds['draw']) / total_prob * 100
                away_prob = (1/best_odds['away']) / total_prob * 100
                
                outcomes = [
                    ('Home Win', home_prob, best_odds['home'], best_bookmaker['home']),
                    ('Draw', draw_prob, best_odds['draw'], best_bookmaker['draw']),
                    ('Away Win', away_prob, best_odds['away'], best_bookmaker['away'])
                ]
                outcomes.sort(key=lambda x: x[1], reverse=True)
                
                # Check for value (crypto-specific)
                crypto_value = 'high'
                if outcomes[0][1] > 60:
                    crypto_value = '🚀 Sniper'
                elif outcomes[0][1] > 50:
                    crypto_value = '🐺 Hunt'
                else:
                    crypto_value = '💀 Risk'
                
                return {
                    'match': f"{match.get('home_team', '')} vs {match.get('away_team', '')}",
                    'league': match.get('sport_title', 'Unknown'),
                    'home_team': match.get('home_team', ''),
                    'away_team': match.get('away_team', ''),
                    'best_odds': best_odds,
                    'best_bookmaker': best_bookmaker,
                    'probabilities': {
                        'home': round(home_prob, 1),
                        'draw': round(draw_prob, 1),
                        'away': round(away_prob, 1)
                    },
                    'prediction': outcomes[0][0],
                    'confidence': round(outcomes[0][1] - outcomes[1][1], 1),
                    'crypto_value': crypto_value,
                    'commence_time': match.get('commence_time')
                }
            
            return None
            
        except Exception as e:
            print(f"Error analyzing crypto bet: {e}")
            return None
    
    def format_crypto_prediction(self, prediction: Dict) -> str:
        """Format prediction with crypto style"""
        emoji = '🐺' if prediction['confidence'] > 15 else '🌙'
        
        message = f"""
{emoji} *WOLF PREDICTION* {emoji}

🔥 *{prediction['match']}*
📊 *League:* {prediction['league']}

*💰 CRYPTO ODDS (USDT)*
🏠 Home: {prediction['best_odds']['home']:.2f} 
   📍 {prediction['best_bookmaker']['home']}
🤝 Draw: {prediction['best_odds']['draw']:.2f}
   📍 {prediction['best_bookmaker']['draw']}
✈️ Away: {prediction['best_odds']['away']:.2f}
   📍 {prediction['best_bookmaker']['away']}

*📊 PROBABILITIES*
🏠 Home: {prediction['probabilities']['home']}%
🤝 Draw: {prediction['probabilities']['draw']}%
✈️ Away: {prediction['probabilities']['away']}%

🎯 *PREDICTION:* {prediction['prediction']}
📈 *CONFIDENCE:* {prediction['confidence']}%

💎 *VALUE:* {prediction['crypto_value']}
"""
        
        if prediction.get('commence_time'):
            try:
                start_time = datetime.fromisoformat(prediction['commence_time'].replace('Z', '+00:00'))
                time_str = start_time.strftime('%Y-%m-%d %H:%M UTC')
                message += f"\n⏰ *Match Time:* {time_str}"
            except:
                pass
        
        message += "\n\n🐺 *WagerWolf* - Hunt the best crypto odds!"
        return message
