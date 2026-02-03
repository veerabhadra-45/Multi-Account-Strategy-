"""
Setup Sample Data for Trading System
Run this to create sample accounts, strategies, and mappings
"""

from models import Database, Account, Strategy, AccountStrategy, Position
from data_service import DataService
import json

def setup_sample_data():
    print("Setting up sample data for trading system...")
    
    # Initialize database and data service
    db = Database()
    data_service = DataService()
    
    # Create sample account
    print("Creating sample account...")
    sample_account = Account(
        broker="ZERODHA",
        api_key="demo_api_key",
        access_token="demo_access_token",
        capital=100000.0,  # 1 Lakh
        max_daily_loss=5000.0,  # 5K daily loss limit
        status="ACTIVE",
        daily_loss=0.0
    )
    account_id = data_service.create_account(sample_account)
    print(f"[OK] Created account with ID: {account_id}")
    
    # Create sample strategies
    print("Creating sample strategies...")
    
    # Strategy 1: Moving Average Crossover
    strategy1 = Strategy(
        name="MA Crossover",
        timeframe="5m",
        parameters=json.dumps({
            "buy_threshold": 2400,
            "sell_threshold": 2600
        }),
        is_active=True
    )
    strategy1_id = data_service.create_strategy(strategy1)
    print(f"[OK] Created strategy 1 with ID: {strategy1_id}")
    
    # Strategy 2: RSI Strategy
    strategy2 = Strategy(
        name="RSI Strategy",
        timeframe="15m",
        parameters=json.dumps({
            "buy_threshold": 2350,
            "sell_threshold": 2650
        }),
        is_active=True
    )
    strategy2_id = data_service.create_strategy(strategy2)
    print(f"[OK] Created strategy 2 with ID: {strategy2_id}")
    
    # Create account-strategy mappings
    print("Creating account-strategy mappings...")
    
    # Mapping 1: 50% allocation to MA Crossover
    mapping1 = AccountStrategy(
        account_id=account_id,
        strategy_id=strategy1_id,
        capital_allocation_percent=50.0,
        max_risk_per_trade=2.0,
        is_enabled=True
    )
    mapping1_id = data_service.create_account_strategy(mapping1)
    print(f"[OK] Created mapping 1 with ID: {mapping1_id}")
    
    # Mapping 2: 30% allocation to RSI Strategy
    mapping2 = AccountStrategy(
        account_id=account_id,
        strategy_id=strategy2_id,
        capital_allocation_percent=30.0,
        max_risk_per_trade=1.5,
        is_enabled=True
    )
    mapping2_id = data_service.create_account_strategy(mapping2)
    print(f"[OK] Created mapping 2 with ID: {mapping2_id}")
    
    # Create sample positions
    print("Creating sample positions...")
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Sample position 1
    cursor.execute("""
        INSERT INTO positions (account_id, strategy_id, symbol, qty, entry_price, pnl)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (account_id, strategy1_id, "RELIANCE", 10, 2450.0, 500.0))
    
    # Sample position 2
    cursor.execute("""
        INSERT INTO positions (account_id, strategy_id, symbol, qty, entry_price, pnl)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (account_id, strategy2_id, "TCS", -5, 3200.0, -250.0))
    
    conn.commit()
    conn.close()
    print("[OK] Created sample positions")
    
    print("\n[SUCCESS] Sample data setup complete!")
    print("\nYou can now:")
    print("1. Run 'python run_strategy_system.py' to start the system")
    print("2. Visit http://localhost:5000 to see the dashboard")
    print("3. View accounts, strategies, mappings, and positions")
    print("4. Start the trading engines to see them in action")

if __name__ == "__main__":
    setup_sample_data()