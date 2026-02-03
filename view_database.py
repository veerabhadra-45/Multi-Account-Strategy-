"""
Database Viewer - Check what data is in your trading database
"""

from data_service import DataService

def view_database():
    print("=== TRADING SYSTEM DATABASE CONTENTS ===\n")
    
    data_service = DataService()
    
    # View accounts
    print("ACCOUNTS:")
    accounts = data_service.get_accounts()
    if accounts:
        for account in accounts:
            print(f"  ID: {account.id}, API Key: {account.api_key}, Capital: ${account.capital:,.2f}, Status: {account.status}")
    else:
        print("  No accounts found")
    
    print("\nSTRATEGIES:")
    strategies = data_service.get_strategies()
    if strategies:
        for strategy in strategies:
            print(f"  ID: {strategy.id}, Name: {strategy.name}, Timeframe: {strategy.timeframe}, Active: {strategy.is_active}")
    else:
        print("  No strategies found")
    
    print("\nACCOUNT-STRATEGY MAPPINGS:")
    mappings = data_service.get_account_strategies()
    if mappings:
        for mapping in mappings:
            print(f"  ID: {mapping['id']}, Account: {mapping['account_name']}, Strategy: {mapping['strategy_name']}")
            print(f"    Capital Allocation: {mapping['capital_allocation_percent']}%, Risk per Trade: {mapping['max_risk_per_trade']}%")
    else:
        print("  No mappings found")
    
    print("\nPOSITIONS:")
    positions = data_service.get_positions()
    if positions:
        for position in positions:
            print(f"  {position['symbol']}: {position['qty']} shares @ ${position['entry_price']}, P&L: ${position['pnl']}")
            print(f"    Account: {position['account_name']}, Strategy: {position['strategy_name']}")
    else:
        print("  No positions found")
    
    print(f"\nTOTAL RECORDS:")
    print(f"  Accounts: {len(accounts)}")
    print(f"  Strategies: {len(strategies)}")
    print(f"  Mappings: {len(mappings)}")
    print(f"  Positions: {len(positions)}")

if __name__ == "__main__":
    view_database()