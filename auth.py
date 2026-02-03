"""
Zerodha Kite Connect Authentication with TOTP
Handles automated login with API credentials and TOTP
"""

import os
import pyotp
import requests
from kiteconnect import KiteConnect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class KiteAuth:
    def __init__(self):
        self.api_key = os.getenv('API_KEY')
        self.api_secret = os.getenv('API_SECRET')
        self.totp_key = os.getenv('TOTP_KEY')
        self.kite = KiteConnect(api_key=self.api_key)
        
        if not all([self.api_key, self.api_secret, self.totp_key]):
            raise ValueError("Missing credentials in .env file")
    
    def generate_totp(self):
        """Generate TOTP code"""
        totp = pyotp.TOTP(self.totp_key)
        return totp.now()
    
    def login_and_get_token(self, user_id, password):
        """Complete login flow with TOTP and get access token"""
        try:
            # Step 1: Get login URL
            login_url = self.kite.login_url()
            
            # Step 2: Simulate login (you'll need to do this manually first time)
            session = requests.Session()
            
            # Get login page
            response = session.get(login_url)
            
            # Login with credentials
            login_data = {
                'user_id': user_id,
                'password': password
            }
            
            login_response = session.post('https://kite.zerodha.com/api/login', data=login_data)
            
            if login_response.status_code == 200:
                # Step 3: Submit TOTP
                totp_code = self.generate_totp()
                totp_data = {
                    'user_id': user_id,
                    'request_id': login_response.json().get('data', {}).get('request_id'),
                    'twofa_value': totp_code
                }
                
                totp_response = session.post('https://kite.zerodha.com/api/twofa', data=totp_data)
                
                if totp_response.status_code == 200:
                    # Extract request token from final redirect
                    request_token = self.extract_request_token(session)
                    
                    if request_token:
                        # Generate session
                        data = self.kite.generate_session(request_token, api_secret=self.api_secret)
                        access_token = data["access_token"]
                        
                        # Save token
                        self.save_access_token(access_token)
                        return access_token
            
            raise Exception("Login failed")
            
        except Exception as e:
            print(f"Automated login failed: {e}")
            return self.manual_login()
    
    def manual_login(self):
        """Fallback manual login method"""
        print("\n=== MANUAL LOGIN REQUIRED ===")
        login_url = self.kite.login_url()
        print(f"1. Visit: {login_url}")
        print("2. Login with your credentials")
        print(f"3. Use TOTP: {self.generate_totp()}")
        print("4. Copy the ENTIRE callback URL")
        
        callback_url = input("Paste the full callback URL: ").strip()
        
        # Extract request_token from URL
        if 'request_token=' in callback_url:
            request_token = callback_url.split('request_token=')[1].split('&')[0]
        else:
            request_token = callback_url  # In case user pastes just the token
        
        if request_token:
            try:
                data = self.kite.generate_session(request_token, api_secret=self.api_secret)
                access_token = data["access_token"]
                self.save_access_token(access_token)
                print("Login successful!")
                return access_token
            except Exception as e:
                print(f"Token generation failed: {e}")
                return None
    
    def save_access_token(self, access_token):
        """Save access token to .env file"""
        with open('.env', 'r') as f:
            content = f.read()
        
        if 'ACCESS_TOKEN=' in content:
            # Update existing token
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('ACCESS_TOKEN='):
                    lines[i] = f'ACCESS_TOKEN={access_token}'
                    break
            content = '\n'.join(lines)
        else:
            # Add new token
            content += f'\nACCESS_TOKEN={access_token}'
        
        with open('.env', 'w') as f:
            f.write(content)
    
    def get_account_name(self, access_token):
        """Get account name from Zerodha API"""
        try:
            self.kite.set_access_token(access_token)
            profile = self.kite.profile()
            return profile.get('user_name', 'Unknown')
        except Exception as e:
            print(f"Failed to get account name: {e}")
            return "Unknown"
        """Return authenticated KiteConnect instance"""
        access_token = os.getenv('ACCESS_TOKEN')
        if not access_token:
            print("❌ No access token found. Running login...")
            access_token = self.manual_login()
            if not access_token:
                print("❌ Authentication failed - no access token")
                return None
        
        try:
            self.kite.set_access_token(access_token)
            # Test the connection
            self.kite.profile()
            return self.kite
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            print("Please run 'python auth.py' to re-authenticate")
            return None

# Quick setup script
if __name__ == "__main__":
    print("🔐 Zerodha Authentication Setup")
    print("Current TOTP:", KiteAuth().generate_totp())
    
    auth = KiteAuth()
    auth.manual_login()