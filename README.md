# Multi-Account Strategy Trading System

A comprehensive Python-based automated trading system that supports multiple Zerodha accounts with strategy execution, risk management, and web-based UI.

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Strategy       │    │  Execution      │    │  Risk           │
│  Engine         │───▶│  Engine         │───▶│  Management     │
│                 │    │                 │    │                 │
│ • Market Data   │    │ • Order Placing │    │ • Daily Limits  │
│ • Signal Gen    │    │ • Position Mgmt │    │ • Per-Trade     │
│ • Multi-Strategy│    │ • Multi-Account │    │ • Capital Alloc │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Web Interface  │
                    │                 │
                    │ • Dashboard     │
                    │ • Account Mgmt  │
                    │ • Strategy Mgmt │
                    │ • Position View │
                    └─────────────────┘
```

## 🎯 Core Features

### Multi-Account Management
- Support for multiple Zerodha trading accounts
- Individual capital allocation and risk limits
- Account-level daily loss monitoring
- Real-time account status tracking

### Strategy Engine
- Automated strategy execution
- Configurable timeframes (1m, 5m, 15m, 1h, 1d)
- Real-time market data processing
- Signal generation and distribution

### Risk Management
- Per-account daily loss limits
- Per-trade risk percentage controls
- Capital allocation management
- Automatic risk checks before order placement

### Web Interface
- Modern Bootstrap-based UI
- Real-time engine status monitoring
- Comprehensive dashboard with analytics
- Easy account and strategy management

## 📁 Project Structure

```
stock-trading/
├── models.py              # Core data models and database
├── data_service.py        # Data access layer (CRUD operations)
├── strategy_engine.py     # Strategy execution engine
├── execution_engine.py    # Order placement and risk management
├── zerodha_service.py     # Zerodha API integration
├── backend_api.py         # Backend API layer
├── strategy_app.py        # Flask web application
├── run_strategy_system.py # System startup script
├── templates/             # HTML templates
│   ├── strategy_base.html
│   ├── strategy_dashboard.html
│   ├── accounts.html
│   ├── strategies.html
│   ├── mappings.html
│   ├── positions.html
│   ├── zerodha_login.html
│   └── zerodha_login_form.html
├── requirements.txt       # Python dependencies
├── .env                  # API credentials
└── trading.db            # SQLite database (auto-created)
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create/update `.env` file:
```env
API_KEY=your_zerodha_api_key
API_SECRET=your_zerodha_api_secret
```

### 3. Start the System
```bash
python run_strategy_system.py
```

### 4. Access Web Interface
Open browser and go to: `http://localhost:5000`

## 📊 System Components

### 1. Account Management
- **Add Accounts**: Configure multiple Zerodha accounts
- **Set Limits**: Define capital and daily loss limits
- **Monitor Status**: Track account health and performance
- **Zerodha Integration**: OAuth login with automatic profile fetching

### 2. Strategy Management
- **Create Strategies**: Define trading logic with parameters
- **Configure Timeframes**: Set execution frequency
- **Activate/Deactivate**: Control strategy execution

### 3. Account-Strategy Mapping
- **Capital Allocation**: Assign percentage of account capital
- **Risk Per Trade**: Set maximum risk per trade
- **Enable/Disable**: Control which strategies run on which accounts

### 4. Position Monitoring
- **Real-time Positions**: View all open positions
- **P&L Tracking**: Monitor profit and loss
- **Strategy Performance**: Analyze performance by strategy

## 🔧 Configuration

### Account Setup Options

#### Option 1: Manual Entry
1. Go to **Accounts** → **Add Account**
2. Enter API key, access token, and account details
3. Set capital amount and daily loss limit

#### Option 2: Zerodha OAuth Login
1. Go to **Accounts** → **Add via Zerodha Login**
2. Enter API key, secret, capital, and loss limits
3. Complete OAuth login flow
4. System automatically fetches account details

### Strategy Creation
1. Go to **Strategies** → **Add Strategy**
2. Define strategy name and timeframe
3. Set buy/sell thresholds
4. Activate strategy

### Account-Strategy Mapping
1. Go to **Mappings** → **Add Mapping**
2. Select account and strategy
3. Set capital allocation percentage
4. Define risk per trade percentage
5. Enable mapping

## 🛡️ Risk Management

### Built-in Safety Features
- **Daily Loss Limits**: Automatic trading halt when limit reached
- **Per-Trade Risk**: Maximum risk per trade as % of allocated capital
- **Capital Allocation**: Prevents over-allocation across strategies
- **Order Quantity Limits**: Caps maximum order size for safety
- **Emergency Stop**: Immediate system shutdown and position closure

### Risk Calculation Example
```
Account Capital: ₹1,00,000
Strategy Allocation: 50% = ₹50,000
Risk Per Trade: 2% = ₹1,000 max loss per trade
```

## 🔄 System Workflow

### 1. Strategy Engine Loop
```python
for strategy in ACTIVE_STRATEGIES:
    data = fetchMarketData(strategy)
    signal = strategy.run(data)
    if signal:
        publish(signal)
```

### 2. Execution Engine Loop
```python
on signal:
    mappings = getAccountStrategies(signal.strategyId)
    for mapping in mappings:
        account = getAccount(mapping.accountId)
        if riskCheck(account, mapping):
            qty = calculateQty(account, mapping)
            placeOrder(account, signal, qty)
```

### 3. Risk Check Logic
```python
def riskCheck(account, mapping):
    if account.dailyLoss > account.maxDailyLoss:
        return False
    if tradeRisk > mapping.maxRiskPerTrade:
        return False
    return True
```

## 📈 Dashboard Features

### System Overview
- Total accounts and active status
- Active strategies count
- Current positions summary
- Real-time engine status

### Performance Analytics
- P&L by strategy
- P&L by account
- Position distribution
- Risk utilization

## 🔌 API Integration

### Zerodha Kite Connect
- Real-time market data
- Order placement and management
- Portfolio and position tracking
- Account information

### Backend API Endpoints
```
POST /api/system/start          # Start trading engines
POST /api/system/stop           # Stop trading engines
GET  /api/system/status         # Get system status
POST /api/system/emergency-stop # Emergency stop
POST /api/accounts/create-zerodha    # Create Zerodha account
GET  /api/accounts/{id}/positions    # Get account positions
POST /api/signals/manual             # Manual signal trigger
GET  /api/pnl/realtime              # Real-time P&L
```

### Database Schema
- **Accounts**: Store account credentials and limits
- **Strategies**: Define trading strategies and parameters
- **AccountStrategies**: Map accounts to strategies with allocation
- **Positions**: Track all trading positions and P&L

## ⚠️ Important Warnings

### Live Trading Risks
- **Real Money**: System uses live trading accounts
- **Start Small**: Begin with minimal capital allocation
- **Monitor Closely**: Always supervise automated trading
- **Test Thoroughly**: Use paper trading for initial testing

### Security Best Practices
- **Never commit credentials** to version control
- **Use environment variables** for sensitive data
- **Regularly rotate API keys**
- **Monitor account access logs**

## 🛠️ Customization

### Adding New Strategies
1. Extend the `run_strategy` method in `strategy_engine.py`
2. Add strategy-specific parameters to the database
3. Update the UI forms to capture new parameters

### Custom Risk Rules
1. Modify `risk_check` method in `execution_engine.py`
2. Add new risk parameters to account/mapping models
3. Update UI to configure new risk parameters

## 📦 Dependencies

```
kiteconnect==4.2.0
python-dotenv==1.0.0
pyotp==2.9.0
requests==2.31.0
flask==3.0.0
selenium==4.15.0
```

## 📞 Support

### Common Issues
1. **Authentication Errors**: Check API credentials in `.env`
2. **Order Failures**: Verify account funds and market hours
3. **Engine Not Starting**: Check database permissions and dependencies
4. **Unicode Errors**: Ensure proper encoding in terminal

### Troubleshooting
- Check browser console for JavaScript errors
- Review Flask application logs
- Verify database file permissions
- Ensure all dependencies are installed

## 🚦 Getting Started Checklist

- [ ] Install Python 3.8+
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create `.env` file with Zerodha API credentials
- [ ] Run system: `python run_strategy_system.py`
- [ ] Access web interface: `http://localhost:5000`
- [ ] Add your first Zerodha account
- [ ] Create a trading strategy
- [ ] Map account to strategy
- [ ] Start trading engines
- [ ] Monitor positions and P&L

## 📄 License

