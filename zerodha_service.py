from kiteconnect import KiteConnect
import os
import requests
import pyotp
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

load_dotenv()

class ZerodhaService:
    def __init__(self, api_key: str, access_token: str = None):
        self.api_key = api_key
        self.kite = KiteConnect(api_key=api_key)
        if access_token:
            self.kite.set_access_token(access_token)
    
    def login_with_credentials(self, user_id: str, password: str, totp_secret: str = None):
        """Login to Zerodha using credentials and OTP"""
        try:
            # Setup Chrome options for headless browsing
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=chrome_options)
            
            # Get login URL
            login_url = self.kite.login_url()
            driver.get(login_url)
            
            # Fill user ID
            user_id_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "userid"))
            )
            user_id_field.send_keys(user_id)
            
            # Fill password
            password_field = driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            
            # Click login button
            login_button = driver.find_element(By.CLASS_NAME, "button-orange")
            login_button.click()
            
            # Wait for OTP page
            time.sleep(3)
            
            # Generate OTP if TOTP secret provided
            if totp_secret:
                totp = pyotp.TOTP(totp_secret)
                otp_code = totp.now()
                
                # Fill OTP
                otp_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "totp"))
                )
                otp_field.send_keys(otp_code)
                
                # Click continue button
                continue_button = driver.find_element(By.CLASS_NAME, "button-orange")
                continue_button.click()
                
                # Wait for redirect and extract request token
                time.sleep(5)
                current_url = driver.current_url
                
                if "request_token=" in current_url:
                    request_token = current_url.split("request_token=")[1].split("&")[0]
                    driver.quit()
                    return {
                        "success": True,
                        "request_token": request_token,
                        "message": "Login successful"
                    }
            
            driver.quit()
            return {
                "success": False,
                "message": "OTP required or login failed",
                "requires_otp": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def login_with_manual_otp(self, user_id: str, password: str):
        """Login and wait for manual OTP entry"""
        try:
            login_url = self.kite.login_url()
            return {
                "success": False,
                "login_url": login_url,
                "message": "Please complete login manually and provide request token",
                "user_id": user_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_session(self, request_token: str, api_secret: str):
        """Generate session using request token"""
        try:
            data = self.kite.generate_session(request_token, api_secret=api_secret)
            self.kite.set_access_token(data["access_token"])
            return data["access_token"]
        except Exception as e:
            print(f"Session generation error: {e}")
            return None
    
    def get_profile(self):
        """Get user profile from Zerodha"""
        try:
            profile = self.kite.profile()
            return {
                'user_name': profile.get('user_name', ''),
                'user_id': profile.get('user_id', ''),
                'email': profile.get('email', ''),
                'broker': profile.get('broker', 'ZERODHA')
            }
        except Exception as e:
            print(f"Error fetching profile: {e}")
            return None
    
    def get_margins(self):
        """Get account margins"""
        try:
            margins = self.kite.margins()
            equity_margin = margins.get('equity', {})
            return {
                'available_cash': equity_margin.get('available', {}).get('cash', 0),
                'net': equity_margin.get('net', 0)
            }
        except Exception as e:
            print(f"Error fetching margins: {e}")
            return None
    
    @staticmethod
    def get_login_url(api_key: str):
        """Get Zerodha login URL"""
        kite = KiteConnect(api_key=api_key)
        return kite.login_url()