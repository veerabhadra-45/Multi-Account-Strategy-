from flask import Flask, jsonify, request
from data_service import DataService
from strategy_engine import StrategyEngine
from execution_engine import ExecutionEngine
from zerodha_service import ZerodhaService
from models import Account, Strategy, AccountStrategy, Signal
import json
import threading
import time

class TradingSystemAPI:
    def __init__(self):
        self.data_service = DataService()
        self.strategy_engine = StrategyEngine()
        self.execution_engine = ExecutionEngine(self.strategy_engine)
        self.running = False
    
    def start_system(self):
        """Start the complete trading system"""
        if not self.running:
            self.strategy_engine.start()
            self.execution_engine.start()
            self.running = True
            return {"status": "success", "message": "Trading system started"}
        return {"status": "error", "message": "System already running"}
    
    def stop_system(self):
        """Stop the complete trading system"""
        if self.running:
            self.strategy_engine.stop()
            self.execution_engine.stop()
            self.running = False
            return {"status": "success", "message": "Trading system stopped"}
        return {"status": "error", "message": "System not running"}
    
    def get_system_status(self):
        """Get overall system status"""
        accounts = self.data_service.get_accounts()
        strategies = self.data_service.get_strategies()
        positions = self.data_service.get_positions()
        
        active_accounts = len([a for a in accounts if a.status == 'ACTIVE'])
        active_strategies = len([s for s in strategies if s.is_active])
        
        return {
            "system_running": self.running,
            "total_accounts": len(accounts),
            "active_accounts": active_accounts,
            "total_strategies": len(strategies),
            "active_strategies": active_strategies,
            "total_positions": len(positions),
            "accounts": [self._account_to_dict(a) for a in accounts],
            "strategies": [self._strategy_to_dict(s) for s in strategies]
        }
    
    def create_account_with_zerodha(self, api_key: str, api_secret: str, capital: float, max_daily_loss: float):
        """Create account using Zerodha API integration"""
        try:
            # Get login URL
            login_url = ZerodhaService.get_login_url(api_key)
            return {
                "status": "pending",
                "login_url": login_url,
                "message": "Complete login and provide request token"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def complete_account_creation(self, api_key: str, api_secret: str, request_token: str, capital: float, max_daily_loss: float):
        """Complete account creation with request token"""
        return self.data_service.complete_account_setup(api_key, api_secret, request_token, capital, max_daily_loss)
    
    def get_account_positions(self, account_id: int):
        """Get positions for specific account"""
        positions = self.data_service.get_positions()
        account_positions = [p for p in positions if p['account_id'] == account_id]
        return {"positions": account_positions}
    
    def get_strategy_performance(self, strategy_id: int):
        """Get performance metrics for a strategy"""
        positions = self.data_service.get_positions()
        strategy_positions = [p for p in positions if p['strategy_id'] == strategy_id]
        
        total_pnl = sum(p['pnl'] for p in strategy_positions)
        total_trades = len(strategy_positions)
        
        return {
            "strategy_id": strategy_id,
            "total_trades": total_trades,
            "total_pnl": total_pnl,
            "positions": strategy_positions
        }
    
    def manual_signal(self, strategy_id: int, symbol: str, action: str, price: float):
        """Manually trigger a trading signal"""
        try:
            signal = Signal(
                strategy_id=strategy_id,
                symbol=symbol,
                action=action,
                price=price,
                timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
            )
            
            self.execution_engine.process_signal(signal)
            return {"status": "success", "message": f"Signal processed: {action} {symbol}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_live_market_data(self, symbol: str):
        """Get live market data for a symbol"""
        # This would integrate with Zerodha API for real data
        # For now, returning mock data
        return {
            "symbol": symbol,
            "ltp": 2500.0,
            "change": 25.0,
            "change_percent": 1.0,
            "volume": 1000000,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def update_risk_parameters(self, account_id: int, max_daily_loss: float = None, capital: float = None):
        """Update risk parameters for an account"""
        try:
            accounts = self.data_service.get_accounts()
            account = next((a for a in accounts if a.id == account_id), None)
            
            if not account:
                return {"status": "error", "message": "Account not found"}
            
            if max_daily_loss is not None:
                account.max_daily_loss = max_daily_loss
            if capital is not None:
                account.capital = capital
            
            self.data_service.update_account(account)
            return {"status": "success", "message": "Risk parameters updated"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_real_time_pnl(self):
        """Get real-time P&L across all accounts"""
        positions = self.data_service.get_positions()
        accounts = self.data_service.get_accounts()
        
        account_pnl = {}
        for account in accounts:
            account_positions = [p for p in positions if p['account_id'] == account.id]
            total_pnl = sum(p['pnl'] for p in account_positions)
            account_pnl[account.id] = {
                "account_name": account.account_name,
                "pnl": total_pnl,
                "daily_loss": account.daily_loss,
                "max_daily_loss": account.max_daily_loss,
                "positions_count": len(account_positions)
            }
        
        return {"account_pnl": account_pnl}
    
    def emergency_stop(self):
        """Emergency stop - close all positions and stop system"""
        try:
            # Stop the system
            self.stop_system()
            
            # In a real implementation, this would close all open positions
            # For now, just mark all accounts as inactive
            accounts = self.data_service.get_accounts()
            for account in accounts:
                account.status = 'INACTIVE'
                self.data_service.update_account(account)
            
            return {"status": "success", "message": "Emergency stop executed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _account_to_dict(self, account: Account):
        """Convert Account object to dictionary"""
        return {
            "id": account.id,
            "account_name": account.account_name,
            "broker": account.broker,
            "capital": account.capital,
            "max_daily_loss": account.max_daily_loss,
            "daily_loss": account.daily_loss,
            "status": account.status
        }
    
    def _strategy_to_dict(self, strategy: Strategy):
        """Convert Strategy object to dictionary"""
        return {
            "id": strategy.id,
            "name": strategy.name,
            "timeframe": strategy.timeframe,
            "parameters": json.loads(strategy.parameters),
            "is_active": strategy.is_active
        }

# Flask API endpoints
app = Flask(__name__)
trading_api = TradingSystemAPI()

@app.route('/api/system/start', methods=['POST'])
def start_system():
    return jsonify(trading_api.start_system())

@app.route('/api/system/stop', methods=['POST'])
def stop_system():
    return jsonify(trading_api.stop_system())

@app.route('/api/system/status', methods=['GET'])
def system_status():
    return jsonify(trading_api.get_system_status())

@app.route('/api/system/emergency-stop', methods=['POST'])
def emergency_stop():
    return jsonify(trading_api.emergency_stop())

@app.route('/api/accounts/create-zerodha', methods=['POST'])
def create_zerodha_account():
    data = request.json
    return jsonify(trading_api.create_account_with_zerodha(
        data['api_key'], data['api_secret'], 
        data['capital'], data['max_daily_loss']
    ))

@app.route('/api/accounts/complete-creation', methods=['POST'])
def complete_account_creation():
    data = request.json
    return jsonify(trading_api.complete_account_creation(
        data['api_key'], data['api_secret'], data['request_token'],
        data['capital'], data['max_daily_loss']
    ))

@app.route('/api/accounts/<int:account_id>/positions', methods=['GET'])
def get_account_positions(account_id):
    return jsonify(trading_api.get_account_positions(account_id))

@app.route('/api/accounts/<int:account_id>/risk', methods=['PUT'])
def update_risk_parameters(account_id):
    data = request.json
    return jsonify(trading_api.update_risk_parameters(
        account_id, data.get('max_daily_loss'), data.get('capital')
    ))

@app.route('/api/strategies/<int:strategy_id>/performance', methods=['GET'])
def get_strategy_performance(strategy_id):
    return jsonify(trading_api.get_strategy_performance(strategy_id))

@app.route('/api/signals/manual', methods=['POST'])
def manual_signal():
    data = request.json
    return jsonify(trading_api.manual_signal(
        data['strategy_id'], data['symbol'], 
        data['action'], data['price']
    ))

@app.route('/api/market/<symbol>', methods=['GET'])
def get_market_data(symbol):
    return jsonify(trading_api.get_live_market_data(symbol))

@app.route('/api/pnl/realtime', methods=['GET'])
def get_realtime_pnl():
    return jsonify(trading_api.get_real_time_pnl())

if __name__ == '__main__':
    app.run(debug=True, port=5001)