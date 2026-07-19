import re
from datetime import datetime
from typing import List, Dict, Any
import hashlib

class Utils:
    """Wolf-themed utilities"""
    
    @staticmethod
    def safe_float(value, default=0.0):
        try:
            return float(value)
        except:
            return default
    
    @staticmethod
    def generate_wallet_address(crypto: str = 'ETH') -> str:
        """Generate a crypto wallet address (mock)"""
        # In production, use web3 or similar
        import secrets
        if crypto == 'ETH':
            return f"0x{secrets.token_hex(40)}"
        elif crypto == 'BTC':
            return f"1{secrets.token_hex(33)}"
        elif crypto == 'SOL':
            return secrets.token_hex(32)
        else:
            return secrets.token_hex(32)
    
    @staticmethod
    def calculate_roi(initial: float, final: float) -> float:
        """Calculate ROI percentage"""
        if initial == 0:
            return 0
        return ((final - initial) / initial) * 100
    
    @staticmethod
    def extract_crypto_from_text(text: str) -> str:
        """Extract cryptocurrency from text"""
        text_lower = text.upper()
        for crypto in ['BTC', 'ETH', 'SOL', 'MATIC', 'USDT']:
            if crypto in text_lower:
                return crypto
        return None
    
    @staticmethod
    def format_crypto_amount(amount: float, crypto: str = 'USDT') -> str:
        """Format crypto amount with proper decimals"""
        if crypto in ['BTC', 'ETH']:
            return f"{amount:.6f} {crypto}"
        else:
            return f"{amount:.2f} {crypto}"
    
    @staticmethod
    def is_valid_crypto_address(address: str, crypto: str = 'ETH') -> bool:
        """Validate crypto address format"""
        if crypto == 'ETH':
            return len(address) == 42 and address.startswith('0x')
        elif crypto == 'BTC':
            return len(address) in [34, 42] and address[0] in ['1', '3']
        elif crypto == 'SOL':
            return len(address) == 44
        else:
            return len(address) > 20
    
    @staticmethod
    def create_wolf_signature() -> str:
        """Create a wolf-themed signature"""
        signatures = [
            "🐺 Hunt the odds, conquer the crypto!",
            "🌙 The wolf never sleeps on opportunity!",
            "🔥 Where others hesitate, wolves feast!",
            "⚡ Speed of the wolf, precision of the hunt!",
            "💀 The market is your hunting ground!"
        ]
        import random
        return random.choice(signatures)
    
    @staticmethod
    def get_wolf_emoji(confidence: float) -> str:
        """Get wolf emoji based on confidence"""
        if confidence > 20:
            return '🐺🔥'  # Alpha wolf
        elif confidence > 10:
            return '🐺🌙'  # Night wolf
        else:
            return '🐺💀'  # Lone wolf
