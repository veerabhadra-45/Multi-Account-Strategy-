import threading
import time
from typing import List
from models import Database, Account, AccountStrategy, Signal, Position
from kiteconnect import KiteConnect
import json

class ExecutionEngine:
    def __init__(self, strategy_engine):
        self.db = Database()
        self.strategy_engine = strategy_engine
        self.running = False
        
    def get_account_strategies(self, strategy_id: int) -> List[AccountStrategy]:
        """Get account strategies for a given strategy ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM account_strategies 
            WHERE strategy_id = ? AND is_enabled = 1
        """, (strategy_id,))
        rows = cursor.fetchall()
        conn.close()
        
        mappings = []
        for row in rows:
            mapping = AccountStrategy(
                id=row[0],
                account_id=row[1],
                strategy_id=row[2],
                capital_allocation_percent=row[3],
                max_risk_per_trade=row[4],
                is_enabled=bool(row[5])
            )
            mappings.append(mapping)
        return mappings
    
    def get_account(self, account_id: int) -> Account:
        """Get account by ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Account(
                id=row[0],
                broker=row[1],
                api_key=row[2],
                access_token=row[3],
                capital=row[4],
                max_daily_loss=row[5],
                status=row[6],
                daily_loss=row[7]
            )
        return None
    
    def risk_check(self, account: Account, mapping: AccountStrategy) -> bool:
        """Perform risk checks before placing order"""
        # Check daily loss limit
        if account.daily_loss > account.max_daily_loss:
            print(f"Account {account.id}: Daily loss limit exceeded")
            return False
        
        # Check per-trade risk limit
        allocated_capital = account.capital * (mapping.capital_allocation_percent / 100)
        trade_risk = allocated_capital * (mapping.max_risk_per_trade / 100)
        
        if trade_risk > allocated_capital:
            print(f"Account {account.id}: Trade risk exceeds allocation")
            return False
        
        return True
    
    def calculate_quantity(self, account: Account, mapping: AccountStrategy, price: float) -> int:
        """Calculate order quantity based on risk parameters"""
        allocated_capital = account.capital * (mapping.capital_allocation_percent / 100)
        trade_risk = allocated_capital * (mapping.max_risk_per_trade / 100)
        
        # Simple quantity calculation - can be enhanced
        quantity = max(1, int(trade_risk / price))
        return min(quantity, 10)  # Cap at 10 shares for safety
    
    def place_order(self, account: Account, signal: Signal, quantity: int):
        """Place order using Zerodha API"""
        try:
            if not account.access_token:
                print(f"Account {account.id}: No access token available")
                return None
            
            kite = KiteConnect(api_key=account.api_key)
            kite.set_access_token(account.access_token)
            
            order_params = {
                "tradingsymbol": signal.symbol,
                "exchange": "NSE",
                "transaction_type": signal.action,
                "quantity": quantity,
                "order_type": "MARKET",
                "product": "MIS",
                "validity": "DAY"
            }
            
            order_id = kite.place_order(**order_params)
            print(f"Order placed: {order_id} for account {account.id}")
            
            # Save position to database
            self.save_position(account.id, signal, quantity)
            
            return order_id
            
        except Exception as e:
            print(f"Order placement failed for account {account.id}: {e}")
            return None
    
    def save_position(self, account_id: int, signal: Signal, quantity: int):
        """Save position to database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        qty = quantity if signal.action == "BUY" else -quantity
        
        cursor.execute("""
            INSERT INTO positions (account_id, strategy_id, symbol, qty, entry_price)
            VALUES (?, ?, ?, ?, ?)
        """, (account_id, signal.strategy_id, signal.symbol, qty, signal.price))
        
        conn.commit()
        conn.close()
    
    def process_signal(self, signal: Signal):
        """Process a trading signal"""
        mappings = self.get_account_strategies(signal.strategy_id)
        
        for mapping in mappings:
            account = self.get_account(mapping.account_id)
            
            if not account or account.status != "ACTIVE":
                continue
            
            if self.risk_check(account, mapping):
                quantity = self.calculate_quantity(account, mapping, signal.price)
                self.place_order(account, signal, quantity)
    
    def start(self):
        """Start the execution engine"""
        self.running = True
        thread = threading.Thread(target=self._run_loop)
        thread.daemon = True
        thread.start()
        print("Execution Engine started")
    
    def stop(self):
        """Stop the execution engine"""
        self.running = False
        print("Execution Engine stopped")
    
    def _run_loop(self):
        """Main execution loop"""
        while self.running:
            try:
                signals = self.strategy_engine.get_pending_signals()
                
                for signal in signals:
                    self.process_signal(signal)
                
                time.sleep(1)  # Check for signals every second
                
            except Exception as e:
                print(f"Execution engine error: {e}")
                time.sleep(5)