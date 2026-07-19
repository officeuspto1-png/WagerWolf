import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List
from config import Config
from database import Database

class OddsSniper:
    """Track and snipe sudden odds movements"""
    
    def __init__(self):
        self.db = Database()
        self.odds_history = {}
        self.sniper_alerts = []
        self.running = False
    
    def start_sniping(self):
        """Start the sniper thread"""
        self.running = True
        thread = threading.Thread(target=self._snipe_loop, daemon=True)
        thread.start()
    
    def stop_sniping(self):
        """Stop the sniper thread"""
        self.running = False
    
    def _snipe_loop(self):
        """Main sniper loop"""
        while self.running:
            try:
                # Fetch latest odds
                matches = self.get_latest_odds()
                
                # Check for significant movements
                for match in matches:
                    self.check_odds_movement(match)
                
                time.sleep(Config.SNIPER_INTERVAL)
            except Exception as e:
                print(f"Sniper error: {e}")
                time.sleep(60)
    
    def get_latest_odds(self):
        """Get latest odds from API"""
        # This would normally fetch from your odds API
        return []
    
    def check_odds_movement(self, match: Dict):
        """Check if odds moved significantly"""
        match_id = match.get('id', '')
        if match_id not in self.odds_history:
            self.odds_history[match_id] = match
            return
        
        previous = self.odds_history[match_id]
        
        # Check for significant moves (>5%)
        for market in match.get('markets', []):
            if market['key'] == 'h2h':
                outcomes = market.get('outcomes', [])
                for outcome in outcomes:
                    name = outcome.get('name', '')
                    current_price = outcome.get('price', 0)
                    
                    # Find previous price
                    prev_price = self.find_previous_price(previous, name)
                    if prev_price > 0:
                        change = ((current_price - prev_price) / prev_price) * 100
                        
                        if abs(change) > 5:  # 5% threshold
                            self.trigger_sniper_alert(match, name, change, current_price)
        
        self.odds_history[match_id] = match
    
    def find_previous_price(self, previous_match: Dict, outcome_name: str) -> float:
        """Find previous price for an outcome"""
        for market in previous_match.get('markets', []):
            if market['key'] == 'h2h':
                for outcome in market.get('outcomes', []):
                    if outcome.get('name', '') == outcome_name:
                        return outcome.get('price', 0)
        return 0
    
    def trigger_sniper_alert(self, match: Dict, outcome: str, change: float, new_price: float):
        """Trigger a sniper alert for users"""
        direction = '📈 UP' if change > 0 else '📉 DOWN'
        emoji = '🔥' if change > 10 else '🐺'
        
        alert = f"""
{emoji} *SNIPER ALERT* {emoji}

🎯 *{match.get('home_team', '')} vs {match.get('away_team', '')}*
📊 *{outcome}*: {direction} {change:.1f}%

💰 *New Price:* {new_price:.2f}
⏰ *Updated:* {datetime.utcnow().strftime('%H:%M UTC')}

💡 *Action:* Hunt this opportunity! 🐺
"""
        # Store for sending to users
        self.sniper_alerts.append({
            'alert': alert,
            'match': match,
            'created_at': datetime.utcnow()
        })
    
    def get_sniper_alerts(self) -> List[Dict]:
        """Get recent sniper alerts"""
        return self.sniper_alerts[-10:]  # Last 10 alerts
