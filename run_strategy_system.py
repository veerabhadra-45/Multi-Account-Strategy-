"""
Multi-Account Strategy Trading System Startup Script
Run this to start the web application
"""

import os
import sys
from models import Database

def initialize_system():
    """Initialize the database and create sample data if needed"""
    print("Initializing Multi-Account Strategy Trading System...")
    
    # Initialize database
    db = Database()
    print("[OK] Database initialized")
    
    # Check if we have any accounts
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM accounts")
    account_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM strategies")
    strategy_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"[OK] Found {account_count} accounts and {strategy_count} strategies")
    
    if account_count == 0:
        print("\nNo accounts found. You'll need to:")
        print("   1. Add your Zerodha account via the web interface")
        print("   2. Create trading strategies")
        print("   3. Map accounts to strategies")
    
    print("\nStarting web application...")
    print("   Access the system at: http://localhost:5000")
    print("   Use Ctrl+C to stop the system")

if __name__ == "__main__":
    try:
        initialize_system()
        
        # Import and run the Flask app
        from strategy_app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n\n[STOP] System stopped by user")
    except Exception as e:
        print(f"\n[ERROR] Error starting system: {e}")
        sys.exit(1)