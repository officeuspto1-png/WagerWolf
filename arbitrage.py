import time
from datetime import datetime, timedelta
from typing import List, Dict
from config import Config
from database import Database

class ArbitrageDetector:
    """Crypto arbitrage detection engine"""
    
    def __init__(self):
        self.db = Database()
        self.threshold = Config.ARBITRAGE_THRESHOLD
    
    def find_arbitrage(self, matches: List[Dict]) -> List[Dict]:
        """Find arbitrage opportunities across different bookmakers"""
        opportunities = []
        
        # Group matches by league and teams
        match_groups = {}
        for match in matches:
            key = f"{match.get('home_team', '')}_{match.get('away_team', '')}"
            if key not in match_groups:
                match_groups[key] = []
            match_groups[key].append(match)
        
        # Check for arbitrage in each group
        for match_id, match_data in match_groups.items():
            if len(match_data) < 2:
                continue
            
            # Get odds from different bookmakers
            odds_data = []
            for match in match_data:
                for bookmaker in match.get('bookmakers', []):
                    if bookmaker['key'] not in Config.CRYPTO_BOOKMAKERS:
                        continue
                    
                    for market in bookmaker.get('markets', []):
                        if market['key'] == 'h2h':
                            outcomes = market.get('outcomes', [])
                            home_price = 0
                            draw_price = 0
                            away_price = 0
                            
                            for outcome in outcomes:
                                name = outcome.get('name', '')
                                price = outcome.get('price', 0)
                                
                                if name == match.get('home_team', ''):
                                    home_price = price
                                elif name == match.get('away_team', ''):
                                    away_price = price
                                elif name == 'Draw':
                                    draw_price = price
                            
                            if home_price > 0 and draw_price > 0 and away_price > 0:
                                # Check for arbitrage using the formula
                                arbitrage_percent = (1/home_price + 1/draw_price + 1/away_price) * 100
                                
                                if arbitrage_percent < 100:
                                    profit = 100 - arbitrage_percent
                                    
                                    if profit >= self.threshold:
                                        opportunities.append({
                                            'match': f"{match.get('home_team', '')} vs {match.get('away_team', '')}",
                                            'league': match.get('sport_title', ''),
                                            'bookmaker': bookmaker['key'],
                                            'home_odds': home_price,
                                            'draw_odds': draw_price,
                                            'away_odds': away_price,
                                            'profit_percentage': round(profit, 2),
                                            'recommended_stake': self.calculate_stake(
                                                home_price, draw_price, away_price
                                            ),
                                            'expires_at': datetime.utcnow() + timedelta(minutes=15)
                                        })
        
        return opportunities
    
    def calculate_stake(self, home_odds, draw_odds, away_odds, total_stake=100):
        """Calculate optimal stake distribution for arbitrage"""
        total_prob = 1/home_odds + 1/draw_odds + 1/away_odds
        
        stakes = {
            'home': (1/home_odds) / total_prob * total_stake,
            'draw': (1/draw_odds) / total_prob * total_stake,
            'away': (1/away_odds) / total_prob * total_stake
        }
        
        return stakes
    
    def format_arbitrage_message(self, opp: Dict) -> str:
        """Format arbitrage opportunity for display"""
        message = f"""
🔄 *ARBITRAGE OPPORTUNITY* 🔄

🐺 *{opp['match']}*
📊 *League:* {opp['league']}
📍 *Bookmaker:* {opp['bookmaker']}

*ODDS*
🏠 Home: {opp['home_odds']:.2f}
🤝 Draw: {opp['draw_odds']:.2f}
✈️ Away: {opp['away_odds']:.2f}

💰 *PROFIT:* {opp['profit_percentage']}%
💎 *ARBITRAGE:* ✅

*Recommended Stakes (100 USDT total):*
🏠 Home: {opp['recommended_stake']['home']:.2f} USDT
🤝 Draw: {opp['recommended_stake']['draw']:.2f} USDT
✈️ Away: {opp['recommended_stake']['away']:.2f} USDT

⏰ *Expires:* {opp['expires_at'].strftime('%H:%M UTC')}

⚠️ *Act fast!* This opportunity won't last!
"""
        return message
