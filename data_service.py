from models import Database, Account, Strategy, AccountStrategy, Position
from zerodha_service import ZerodhaService
from typing import List, Optional

class DataService:
    def __init__(self):
        self.db = Database()
    
    # Account operations
    def create_account(self, account: Account) -> int:
        # Fetch account name from Zerodha if access_token is provided
        if account.access_token:
            try:
                zerodha = ZerodhaService(account.api_key, account.access_token)
                profile = zerodha.get_profile()
                if profile:
                    account.account_name = profile['user_name'] or profile['user_id']
            except Exception as e:
                print(f"Could not fetch account name from Zerodha: {e}")
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO accounts (broker, api_key, access_token, account_name, capital, max_daily_loss, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (account.broker, account.api_key, account.access_token, account.account_name,
              account.capital, account.max_daily_loss, account.status))
        account_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return account_id
    
    def get_accounts(self) -> List[Account]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, broker, api_key, access_token, account_name, capital, max_daily_loss, status, daily_loss FROM accounts")
        rows = cursor.fetchall()
        conn.close()
        
        accounts = []
        for row in rows:
            account = Account(
                id=row[0], broker=row[1], api_key=row[2], access_token=row[3],
                account_name=row[4] or "", capital=float(row[5] or 0), 
                max_daily_loss=float(row[6] or 0), status=row[7], 
                daily_loss=float(row[8] or 0)
            )
            accounts.append(account)
        return accounts
    
    def update_account(self, account: Account):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE accounts SET broker=?, api_key=?, access_token=?, account_name=?, capital=?, 
            max_daily_loss=?, status=?, daily_loss=? WHERE id=?
        """, (account.broker, account.api_key, account.access_token, account.account_name, account.capital,
              account.max_daily_loss, account.status, account.daily_loss, account.id))
        conn.commit()
        conn.close()
    
    def add_account_with_login(self, api_key: str, api_secret: str, user_id: str, password: str, totp_key: str = None):
        """Add account by logging in with Zerodha credentials"""
        try:
            zerodha = ZerodhaService(api_key)
            
            # For now, we'll use the manual OAuth flow
            # Get login URL for user to complete authentication
            login_url = ZerodhaService.get_login_url(api_key)
            
            return {
                'success': False,
                'login_url': login_url,
                'message': 'Please complete login at the provided URL and get request token'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def complete_account_setup(self, api_key: str, api_secret: str, request_token: str, capital: float, max_daily_loss: float):
        """Complete account setup with request token"""
        try:
            zerodha = ZerodhaService(api_key)
            access_token = zerodha.generate_session(request_token, api_secret)
            
            if access_token:
                profile = zerodha.get_profile()
                if profile:
                    account = Account(
                        broker='ZERODHA',
                        api_key=api_key,
                        access_token=access_token,
                        account_name=profile['user_name'] or profile['user_id'],
                        capital=capital,
                        max_daily_loss=max_daily_loss,
                        status='ACTIVE'
                    )
                    account_id = self.create_account(account)
                    return {
                        'success': True,
                        'account_id': account_id,
                        'account_name': account.account_name
                    }
            
            return {
                'success': False,
                'error': 'Failed to generate access token or fetch profile'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def login_with_zerodha_credentials(self, api_key: str, api_secret: str, user_id: str, password: str, totp_secret: str, capital: float, max_daily_loss: float):
        """Complete login with Zerodha credentials and OTP"""
        try:
            zerodha = ZerodhaService(api_key)
            login_result = zerodha.login_with_credentials(user_id, password, totp_secret)
            
            if login_result['success']:
                access_token = zerodha.generate_session(login_result['request_token'], api_secret)
                
                if access_token:
                    profile = zerodha.get_profile()
                    if profile:
                        account = Account(
                            broker='ZERODHA',
                            api_key=api_key,
                            access_token=access_token,
                            account_name=profile['user_name'] or profile['user_id'],
                            capital=capital,
                            max_daily_loss=max_daily_loss,
                            status='ACTIVE'
                        )
                        account_id = self.create_account(account)
                        return {
                            'success': True,
                            'account_id': account_id,
                            'account_name': account.account_name
                        }
            
            return login_result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_account(self, account_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM accounts WHERE id=?", (account_id,))
        conn.commit()
        conn.close()
    
    # Strategy operations
    def create_strategy(self, strategy: Strategy) -> int:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO strategies (name, timeframe, parameters, is_active)
            VALUES (?, ?, ?, ?)
        """, (strategy.name, strategy.timeframe, strategy.parameters, strategy.is_active))
        strategy_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return strategy_id
    
    def get_strategies(self) -> List[Strategy]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM strategies")
        rows = cursor.fetchall()
        conn.close()
        
        strategies = []
        for row in rows:
            strategy = Strategy(
                id=row[0], name=row[1], timeframe=row[2], 
                parameters=row[3], is_active=bool(row[4])
            )
            strategies.append(strategy)
        return strategies
    
    def update_strategy(self, strategy: Strategy):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE strategies SET name=?, timeframe=?, parameters=?, is_active=? WHERE id=?
        """, (strategy.name, strategy.timeframe, strategy.parameters, strategy.is_active, strategy.id))
        conn.commit()
        conn.close()
    
    def delete_strategy(self, strategy_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM strategies WHERE id=?", (strategy_id,))
        conn.commit()
        conn.close()
    
    # Account-Strategy mapping operations
    def create_account_strategy(self, mapping: AccountStrategy) -> int:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO account_strategies (account_id, strategy_id, capital_allocation_percent, 
            max_risk_per_trade, is_enabled) VALUES (?, ?, ?, ?, ?)
        """, (mapping.account_id, mapping.strategy_id, mapping.capital_allocation_percent,
              mapping.max_risk_per_trade, mapping.is_enabled))
        mapping_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return mapping_id
    
    def get_account_strategies(self) -> List[dict]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT acs.*, a.account_name, s.name as strategy_name
            FROM account_strategies acs
            JOIN accounts a ON acs.account_id = a.id
            JOIN strategies s ON acs.strategy_id = s.id
        """)
        rows = cursor.fetchall()
        conn.close()
        
        mappings = []
        for row in rows:
            mapping = {
                'id': row[0],
                'account_id': row[1],
                'strategy_id': row[2],
                'capital_allocation_percent': float(row[3] or 0),
                'max_risk_per_trade': float(row[4] or 0),
                'is_enabled': bool(row[5]),
                'account_name': row[6] or "",
                'strategy_name': row[7] or ""
            }
            mappings.append(mapping)
        return mappings
    
    def update_account_strategy(self, mapping: AccountStrategy):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE account_strategies SET account_id=?, strategy_id=?, 
            capital_allocation_percent=?, max_risk_per_trade=?, is_enabled=? WHERE id=?
        """, (mapping.account_id, mapping.strategy_id, mapping.capital_allocation_percent,
              mapping.max_risk_per_trade, mapping.is_enabled, mapping.id))
        conn.commit()
        conn.close()
    
    def delete_account_strategy(self, mapping_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM account_strategies WHERE id=?", (mapping_id,))
        conn.commit()
        conn.close()
    
    # Position operations
    def get_positions(self) -> List[dict]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, a.account_name, s.name as strategy_name
            FROM positions p
            JOIN accounts a ON p.account_id = a.id
            JOIN strategies s ON p.strategy_id = s.id
            ORDER BY p.created_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        
        positions = []
        for row in rows:
            position = {
                'id': row[0],
                'account_id': row[1],
                'strategy_id': row[2],
                'symbol': row[3] or "",
                'qty': int(row[4] or 0),
                'entry_price': float(row[5] or 0),
                'pnl': float(row[6] or 0),
                'created_at': row[7] or "",
                'account_name': row[8] or "",
                'strategy_name': row[9] or ""
            }
            positions.append(position)
        return positions