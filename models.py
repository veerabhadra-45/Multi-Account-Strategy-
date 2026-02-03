from dataclasses import dataclass
from typing import Optional, List
from enum import Enum
import sqlite3
import json
from datetime import datetime

class BrokerType(Enum):
    ZERODHA = "ZERODHA"

class AccountStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

@dataclass
class Account:
    id: Optional[int] = None
    broker: str = BrokerType.ZERODHA.value
    api_key: str = ""
    access_token: str = ""
    account_name: str = ""
    capital: float = 0.0
    max_daily_loss: float = 0.0
    status: str = AccountStatus.ACTIVE.value
    daily_loss: float = 0.0

@dataclass
class Strategy:
    id: Optional[int] = None
    name: str = ""
    timeframe: str = ""
    parameters: str = "{}"
    is_active: bool = True

@dataclass
class AccountStrategy:
    id: Optional[int] = None
    account_id: int = 0
    strategy_id: int = 0
    capital_allocation_percent: float = 0.0
    max_risk_per_trade: float = 0.0
    is_enabled: bool = True

@dataclass
class Position:
    id: Optional[int] = None
    account_id: int = 0
    strategy_id: int = 0
    symbol: str = ""
    qty: int = 0
    entry_price: float = 0.0
    pnl: float = 0.0
    created_at: str = ""

@dataclass
class Signal:
    strategy_id: int
    symbol: str
    action: str  # BUY/SELL
    price: float
    timestamp: str

class Database:
    def __init__(self, db_path="trading.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                broker TEXT NOT NULL,
                api_key TEXT NOT NULL,
                access_token TEXT,
                account_name TEXT,
                capital REAL DEFAULT 0,
                max_daily_loss REAL DEFAULT 0,
                status TEXT DEFAULT 'ACTIVE',
                daily_loss REAL DEFAULT 0
            )
        ''')
        
        # Add account_name column if it doesn't exist (for existing databases)
        try:
            cursor.execute('ALTER TABLE accounts ADD COLUMN account_name TEXT')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Strategies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                timeframe TEXT,
                parameters TEXT DEFAULT '{}',
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Account-Strategy mapping
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account_strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                strategy_id INTEGER,
                capital_allocation_percent REAL DEFAULT 0,
                max_risk_per_trade REAL DEFAULT 0,
                is_enabled BOOLEAN DEFAULT 1,
                FOREIGN KEY (account_id) REFERENCES accounts (id),
                FOREIGN KEY (strategy_id) REFERENCES strategies (id)
            )
        ''')
        
        # Positions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                strategy_id INTEGER,
                symbol TEXT,
                qty INTEGER,
                entry_price REAL,
                pnl REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts (id),
                FOREIGN KEY (strategy_id) REFERENCES strategies (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)