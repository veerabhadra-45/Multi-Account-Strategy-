from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import Account, Strategy, AccountStrategy
from data_service import DataService
from backend_api import TradingSystemAPI
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Add JSON filter for templates
@app.template_filter('from_json')
def from_json_filter(value):
    try:
        return json.loads(value)
    except:
        return {}

# Initialize services
data_service = DataService()
trading_api = TradingSystemAPI()

# Global engine state
engines_running = False

@app.route('/')
def dashboard():
    accounts = data_service.get_accounts()
    strategies = data_service.get_strategies()
    mappings = data_service.get_account_strategies()
    positions = data_service.get_positions()
    
    return render_template('strategy_dashboard.html', 
                         accounts=accounts, 
                         strategies=strategies,
                         mappings=mappings,
                         positions=positions,
                         engines_running=engines_running)

# Account Management
@app.route('/accounts')
def accounts():
    accounts = data_service.get_accounts()
    return render_template('accounts.html', accounts=accounts)

@app.route('/accounts/add', methods=['GET', 'POST'])
def add_account():
    if request.method == 'POST':
        access_token = request.form.get('access_token', '')
        account_name = "Unknown"
        
        # Try to get account name if access token provided
        if access_token:
            try:
                auth = KiteAuth()
                account_name = auth.get_account_name(access_token)
            except:
                pass
        
        account = Account(
            broker=request.form['broker'],
            api_key=request.form['api_key'],
            access_token=access_token,
            account_name=account_name,
            capital=float(request.form['capital']),
            max_daily_loss=float(request.form['max_daily_loss']),
            status=request.form['status']
        )
        data_service.create_account(account)
        flash('Account added successfully!', 'success')
        return redirect(url_for('accounts'))
    
    return render_template('add_account.html')

@app.route('/accounts/edit/<int:account_id>', methods=['GET', 'POST'])
def edit_account(account_id):
    accounts = data_service.get_accounts()
    account = next((a for a in accounts if a.id == account_id), None)
    
    if not account:
        flash('Account not found!', 'error')
        return redirect(url_for('accounts'))
    
    if request.method == 'POST':
        access_token = request.form.get('access_token', '')
        account_name = account.account_name
        
        # Update account name if access token changed
        if access_token and access_token != account.access_token:
            try:
                auth = KiteAuth()
                account_name = auth.get_account_name(access_token)
            except:
                pass
        
        account.broker = request.form['broker']
        account.api_key = request.form['api_key']
        account.access_token = access_token
        account.account_name = account_name
        account.capital = float(request.form['capital'])
        account.max_daily_loss = float(request.form['max_daily_loss'])
        account.status = request.form['status']
        
        data_service.update_account(account)
        flash('Account updated successfully!', 'success')
        return redirect(url_for('accounts'))
    
    return render_template('edit_account.html', account=account)

@app.route('/accounts/zerodha-login', methods=['GET', 'POST'])
def zerodha_login():
    if request.method == 'POST':
        api_key = request.form['api_key']
        api_secret = request.form['api_secret']
        capital = float(request.form['capital'])
        max_daily_loss = float(request.form['max_daily_loss'])
        
        # Get login URL
        result = data_service.add_account_with_login(api_key, api_secret, '', '')
        
        if 'login_url' in result:
            # Store form data in session for later use
            from flask import session
            session['pending_account'] = {
                'api_key': api_key,
                'api_secret': api_secret,
                'capital': capital,
                'max_daily_loss': max_daily_loss
            }
            return render_template('zerodha_login.html', login_url=result['login_url'])
        else:
            flash(f'Error: {result.get("error", "Unknown error")}', 'error')
    
    return render_template('zerodha_login_form.html')

@app.route('/accounts/complete-setup', methods=['POST'])
def complete_account_setup():
    from flask import session
    request_token = request.form['request_token']
    
    if 'pending_account' not in session:
        flash('No pending account setup found!', 'error')
        return redirect(url_for('accounts'))
    
    pending = session['pending_account']
    result = data_service.complete_account_setup(
        pending['api_key'],
        pending['api_secret'],
        request_token,
        pending['capital'],
        pending['max_daily_loss']
    )
    
    if result['success']:
        flash(f'Account {result["account_name"]} added successfully!', 'success')
        session.pop('pending_account', None)
    else:
        flash(f'Error: {result["error"]}', 'error')
    
    return redirect(url_for('accounts'))

@app.route('/accounts/delete/<int:account_id>')
def delete_account(account_id):
    data_service.delete_account(account_id)
    flash('Account deleted successfully!', 'success')
    return redirect(url_for('accounts'))

# Strategy Management
@app.route('/strategies')
def strategies():
    strategies = data_service.get_strategies()
    return render_template('strategies.html', strategies=strategies)

@app.route('/strategies/add', methods=['GET', 'POST'])
def add_strategy():
    if request.method == 'POST':
        parameters = {
            'buy_threshold': float(request.form.get('buy_threshold', 0)),
            'sell_threshold': float(request.form.get('sell_threshold', 0))
        }
        
        strategy = Strategy(
            name=request.form['name'],
            timeframe=request.form['timeframe'],
            parameters=json.dumps(parameters),
            is_active=bool(request.form.get('is_active'))
        )
        data_service.create_strategy(strategy)
        flash('Strategy added successfully!', 'success')
        return redirect(url_for('strategies'))
    
    return render_template('add_strategy.html')

@app.route('/strategies/edit/<int:strategy_id>', methods=['GET', 'POST'])
def edit_strategy(strategy_id):
    strategies = data_service.get_strategies()
    strategy = next((s for s in strategies if s.id == strategy_id), None)
    
    if not strategy:
        flash('Strategy not found!', 'error')
        return redirect(url_for('strategies'))
    
    if request.method == 'POST':
        parameters = {
            'buy_threshold': float(request.form.get('buy_threshold', 0)),
            'sell_threshold': float(request.form.get('sell_threshold', 0))
        }
        
        strategy.name = request.form['name']
        strategy.timeframe = request.form['timeframe']
        strategy.parameters = json.dumps(parameters)
        strategy.is_active = bool(request.form.get('is_active'))
        
        data_service.update_strategy(strategy)
        flash('Strategy updated successfully!', 'success')
        return redirect(url_for('strategies'))
    
    # Parse parameters for form
    params = json.loads(strategy.parameters)
    return render_template('edit_strategy.html', strategy=strategy, params=params)

@app.route('/strategies/delete/<int:strategy_id>')
def delete_strategy(strategy_id):
    data_service.delete_strategy(strategy_id)
    flash('Strategy deleted successfully!', 'success')
    return redirect(url_for('strategies'))

# Account-Strategy Mapping
@app.route('/mappings')
def mappings():
    mappings = data_service.get_account_strategies()
    accounts = data_service.get_accounts()
    strategies = data_service.get_strategies()
    return render_template('mappings.html', mappings=mappings, accounts=accounts, strategies=strategies)

@app.route('/mappings/add', methods=['GET', 'POST'])
def add_mapping():
    if request.method == 'POST':
        mapping = AccountStrategy(
            account_id=int(request.form['account_id']),
            strategy_id=int(request.form['strategy_id']),
            capital_allocation_percent=float(request.form['capital_allocation_percent']),
            max_risk_per_trade=float(request.form['max_risk_per_trade']),
            is_enabled=bool(request.form.get('is_enabled'))
        )
        data_service.create_account_strategy(mapping)
        flash('Mapping added successfully!', 'success')
        return redirect(url_for('mappings'))
    
    accounts = data_service.get_accounts()
    strategies = data_service.get_strategies()
    return render_template('add_mapping.html', accounts=accounts, strategies=strategies)

@app.route('/mappings/delete/<int:mapping_id>')
def delete_mapping(mapping_id):
    data_service.delete_account_strategy(mapping_id)
    flash('Mapping deleted successfully!', 'success')
    return redirect(url_for('mappings'))

# Positions
@app.route('/positions')
def positions():
    positions = data_service.get_positions()
    return render_template('positions.html', positions=positions)

# Engine Control
@app.route('/engines/start')
def start_engines():
    global engines_running
    if not engines_running:
        result = trading_api.start_system()
        if result['status'] == 'success':
            engines_running = True
            flash('Trading engines started!', 'success')
        else:
            flash(f'Error: {result["message"]}', 'error')
    else:
        flash('Engines are already running!', 'warning')
    return redirect(url_for('dashboard'))

@app.route('/engines/stop')
def stop_engines():
    global engines_running
    if engines_running:
        result = trading_api.stop_system()
        if result['status'] == 'success':
            engines_running = False
            flash('Trading engines stopped!', 'success')
        else:
            flash(f'Error: {result["message"]}', 'error')
    else:
        flash('Engines are not running!', 'warning')
    return redirect(url_for('dashboard'))

# API endpoints for real-time updates
@app.route('/api/status')
def api_status():
    system_status = trading_api.get_system_status()
    return jsonify({
        'engines_running': system_status['system_running'],
        'active_strategies': system_status['active_strategies'],
        'active_accounts': system_status['active_accounts'],
        'total_positions': system_status['total_positions']
    })

@app.route('/api/pnl')
def api_pnl():
    return jsonify(trading_api.get_real_time_pnl())

@app.route('/api/emergency-stop', methods=['POST'])
def api_emergency_stop():
    result = trading_api.emergency_stop()
    global engines_running
    if result['status'] == 'success':
        engines_running = False
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)