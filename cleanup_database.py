"""
Database Cleanup Script
Removes all data from the trading database
"""

from models import Database

def cleanup_database():
    print("Cleaning up database...")
    
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Delete all data from tables (in correct order due to foreign keys)
    print("Removing positions...")
    cursor.execute("DELETE FROM positions")
    
    print("Removing account-strategy mappings...")
    cursor.execute("DELETE FROM account_strategies")
    
    print("Removing strategies...")
    cursor.execute("DELETE FROM strategies")
    
    print("Removing accounts...")
    cursor.execute("DELETE FROM accounts")
    
    # Reset auto-increment counters
    cursor.execute("DELETE FROM sqlite_sequence")
    
    conn.commit()
    conn.close()
    
    print("\n[SUCCESS] Database cleaned up!")
    print("All accounts, strategies, mappings, and positions have been removed.")
    print("You now have a fresh, empty database.")

if __name__ == "__main__":
    cleanup_database()