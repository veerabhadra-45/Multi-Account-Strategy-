import threading
import time
from typing import List, Dict
from models import Database, Strategy, Signal, Account
from datetime import datetime
import json

class StrategyEngine:
    def __init__(self):
        self.db = Database()
        self.running = False
        self.signals = []
        
    def fetch_market_data(self, strategy: Strategy) -> Dict:
        """Fetch market data for strategy - placeholder implementation"""
        # In real implementation, this would fetch from Zerodha API
        return {
            "symbol": "RELIANCE",
            "price": 2500.0,
            "volume": 1000,
            "timestamp": datetime.now().isoformat()
        }
    
    def run_strategy(self, strategy: Strategy, data: Dict) -> Signal:
        """Run strategy logic - placeholder implementation"""
        # Simple moving average crossover strategy example
        params = json.loads(strategy.parameters)
        
        # Placeholder logic - in real implementation, this would be strategy-specific
        if data["price"] > params.get("buy_threshold", 2400):
            return Signal(
                strategy_id=strategy.id,
                symbol=data["symbol"],
                action="BUY",
                price=data["price"],
                timestamp=data["timestamp"]
            )
        elif data["price"] < params.get("sell_threshold", 2600):
            return Signal(
                strategy_id=strategy.id,
                symbol=data["symbol"],
                action="SELL",
                price=data["price"],
                timestamp=data["timestamp"]
            )
        return None
    
    def get_active_strategies(self) -> List[Strategy]:
        """Get all active strategies from database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM strategies WHERE is_active = 1")
        rows = cursor.fetchall()
        conn.close()
        
        strategies = []
        for row in rows:
            strategy = Strategy(
                id=row[0],
                name=row[1],
                timeframe=row[2],
                parameters=row[3],
                is_active=bool(row[4])
            )
            strategies.append(strategy)
        return strategies
    
    def publish_signal(self, signal: Signal):
        """Publish signal to execution engine"""
        self.signals.append(signal)
        print(f"Signal published: {signal.action} {signal.symbol} at {signal.price}")
    
    def start(self):
        """Start the strategy engine"""
        self.running = True
        thread = threading.Thread(target=self._run_loop)
        thread.daemon = True
        thread.start()
        print("Strategy Engine started")
    
    def stop(self):
        """Stop the strategy engine"""
        self.running = False
        print("Strategy Engine stopped")
    
    def _run_loop(self):
        """Main strategy execution loop"""
        while self.running:
            try:
                active_strategies = self.get_active_strategies()
                
                for strategy in active_strategies:
                    data = self.fetch_market_data(strategy)
                    signal = self.run_strategy(strategy, data)
                    
                    if signal:
                        self.publish_signal(signal)
                
                time.sleep(5)  # Run every 5 seconds
                
            except Exception as e:
                print(f"Strategy engine error: {e}")
                time.sleep(10)
    
    def get_pending_signals(self) -> List[Signal]:
        """Get and clear pending signals"""
        signals = self.signals.copy()
        self.signals.clear()
        return signals