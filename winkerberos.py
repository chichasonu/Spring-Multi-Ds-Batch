import winkerberos
import requests
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
import json

class WinKerberosWebDriver:
    def __init__(self, username, password, domain):
        self.username = username
        self.password = password
        self.domain = domain
        self.driver = None
        self.kerberos_context = None
        
    def authenticate_with_kerberos(self, service_principal, target_url):
        """
        Perform Kerberos authentication using winkerberos and get cookies
        """
        try:
            # Initialize Kerberos context
            result, self.kerberos_context = winkerberos.authGSSClientInit(
                service_principal,
                gssflags=winkerberos.GSS_C_MUTUAL_FLAG | winkerberos.GSS_C_SEQUENCE_FLAG,
                username=f"{self.domain}\\{self.username}",
                password=self.password
            )
            
            if result != winkerberos.AUTH_GSS_COMPLETE:
                print("Failed to initialize Kerberos context")
                return None
            
            # Start the authentication process
            result = winkerberos.authGSSClientStep(self.kerberos_context, "")
            
            if result == winkerberos.AUTH_GSS_CONTINUE:
                # Get the authentication token
                token = winkerberos.authGSSClientResponse(self.kerberos_context)
                
                # Make HTTP request with Negotiate header
                cookies = self._make_authenticated_request(token, target_url)
                return cookies
            else:
                print("Kerberos authentication step failed")
                return None
                
        except Exception as e:
            print(f"Kerberos authentication error: {str(e)}")
            return None
    
    def _make_authenticated_request(self, kerberos_token, target_url):
        """
        Make HTTP request with Kerberos token to get session cookies
        """
        try:
            headers = {
                'Authorization': f'Negotiate {kerberos_token}',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            session = requests.Session()
            response = session.get(target_url, headers=headers, verify=False)
            
            print(f"Authentication request status: {response.status_code}")
            
            if response.status_code == 200:
                print("Kerberos authentication successful")
                return session.cookies
            elif response.status_code == 401:
                # Handle challenge-response if needed
                www_authenticate = response.headers.get('WWW-Authenticate', '')
                if 'Negotiate' in www_authenticate:
                    challenge = www_authenticate.replace('Negotiate ', '')
                    return self._handle_kerberos_challenge(challenge, target_url, session)
            
            print(f"Authentication failed with status: {response.status_code}")
            return None
            
        except Exception as e:
            print(f"HTTP request error: {str(e)}")
            return None
    
    def _handle_kerberos_challenge(self, challenge, target_url, session):
        """
        Handle Kerberos challenge-response authentication
        """
        try:
            # Process the challenge
            result = winkerberos.authGSSClientStep(self.kerberos_context, challenge)
            
            if result == winkerberos.AUTH_GSS_COMPLETE:
                # Get the response token
                response_token = winkerberos.authGSSClientResponse(self.kerberos_context)
                
                headers = {
                    'Authorization': f'Negotiate {response_token}',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = session.get(target_url, headers=headers, verify=False)
                
                if response.status_code == 200:
                    print("Challenge-response authentication successful")
                    return session.cookies
                    
            print("Challenge-response authentication failed")
            return None
            
        except Exception as e:
            print(f"Challenge handling error: {str(e)}")
            return None
    
    def setup_webdriver(self, headless=False):
        """
        Setup Chrome WebDriver with Kerberos-friendly options
        """
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument("--headless")
        
        # Chrome options for Kerberos authentication
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        
        # Kerberos-specific options
        chrome_options.add_argument("--auth-server-whitelist=*")
        chrome_options.add_argument("--auth-negotiate-delegate-whitelist=*")
        chrome_options.add_argument("--enable-auth-negotiate-port")
        
        # User agent
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        print("WebDriver initialized successfully")
        return self.driver
    
    def add_cookies_to_browser(self, cookies, target_url):
        """
        Add authentication cookies to Selenium WebDriver
        """
        try:
            # Navigate to the domain first to set cookies
            parsed_url = urlparse(target_url)
            domain_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            print(f"Navigating to domain: {domain_url}")
            self.driver.get(domain_url)
            
            # Add each cookie to the browser
            for cookie in cookies:
                cookie_dict = {
                    'name': cookie.name,
                    'value': cookie.value,
                    'domain': cookie.domain if cookie.domain else parsed_url.netloc,
                    'path': cookie.path if cookie.path else '/',
                    'secure': getattr(cookie, 'secure', False)
                }
                
                # Remove leading dot from domain if present for Selenium
                if cookie_dict['domain'].startswith('.'):
                    cookie_dict['domain'] = cookie_dict['domain'][1:]
                
                try:
                    self.driver.add_cookie(cookie_dict)
                    print(f"Added cookie: {cookie.name} = {cookie.value[:20]}...")
                except Exception as e:
                    print(f"Failed to add cookie {cookie.name}: {str(e)}")
            
            print("All cookies added successfully")
            return True
            
        except Exception as e:
            print(f"Error adding cookies to browser: {str(e)}")
            return False
    
    def navigate_with_kerberos_auth(self, service_principal, target_url):
        """
        Complete authentication and navigation flow
        """
        try:
            print("Starting Kerberos authentication process...")
            
            # Step 1: Perform Kerberos authentication
            cookies = self.authenticate_with_kerberos(service_principal, target_url)
            
            if not cookies:
                print("Failed to obtain authentication cookies")
                return False
            
            print(f"Obtained {len(cookies)} authentication cookies")
            
            # Step 2: Setup WebDriver
            print("Setting up Selenium WebDriver...")
            self.setup_webdriver()
            
            # Step 3: Add cookies to browser
            print("Adding authentication cookies to browser...")
            if not self.add_cookies_to_browser(cookies, target_url):
                return False
            
            # Step 4: Navigate to target URL
            print(f"Navigating to authenticated page: {target_url}")
            self.driver.get(target_url)
            
            # Verify successful authentication
            current_url = self.driver.current_url
            print(f"Current URL after navigation: {current_url}")
            
            # Check if we're redirected to login page (sign of failed auth)
            if 'login' in current_url.lower() or 'auth' in current_url.lower():
                print("Warning: May have been redirected to login page")
                return False
            
            print("Successfully authenticated and navigated!")
            return True
            
        except Exception as e:
            print(f"Error in authentication flow: {str(e)}")
            return False
    
    def wait_for_element(self, locator_type, locator_value, timeout=10):
        """
        Wait for an element to be present
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((locator_type, locator_value)))
            return element
        except Exception as e:
            print(f"Element not found: {str(e)}")
            return None
    
    def cleanup(self):
        """
        Clean up resources
        """
        try:
            if self.kerberos_context:
                winkerberos.authGSSClientClean(self.kerberos_context)
                print("Kerberos context cleaned up")
        except:
            pass
        
        if self.driver:
            self.driver.quit()
            print("WebDriver closed")

# Usage example
def main():
    # Configuration - Replace with your actual values
    USERNAME = "your_username"
    PASSWORD = "your_password"
    DOMAIN = "YOUR_DOMAIN"  # e.g., "COMPANY"
    
    # Service Principal Name (SPN) - Format: HTTP/hostname or HTTP/fqdn
    SERVICE_PRINCIPAL = "HTTP/your-server.your-domain.com"
    
    # Target URL
    TARGET_URL = "https://your-server.your-domain.com/protected-page"
    
    # Create Kerberos WebDriver instance
    kerberos_driver = WinKerberosWebDriver(USERNAME, PASSWORD, DOMAIN)
    
    try:
        # Perform authentication and navigation
        success = kerberos_driver.navigate_with_kerberos_auth(SERVICE_PRINCIPAL, TARGET_URL)
        
        if success:
            print("\n=== Authentication Successful! ===")
            
            # Example: Wait for a specific element and interact with it
            # element = kerberos_driver.wait_for_element(By.ID, "welcome-message")
            # if element:
            #     print(f"Found element with text: {element.text}")
            
            # Example: Get page title
            print(f"Page title: {kerberos_driver.driver.title}")
            
            # Example: Take a screenshot
            kerberos_driver.driver.save_screenshot("authenticated_page.png")
            print("Screenshot saved as 'authenticated_page.png'")
            
            # Keep browser open for manual inspection
            input("\nPress Enter to close the browser...")
            
        else:
            print("Authentication failed!")
            
    except KeyboardInterrupt:
        print("\nOperation interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    finally:
        print("Cleaning up...")
        kerberos_driver.cleanup()

# Alternative function for custom cookie handling
def add_custom_kerberos_cookies(driver, auth_cookies_dict):
    """
    Add custom cookies if you have them in dictionary format
    """
    cookies_to_add = [
        {
            'name': 'KRB_AUTH',
            'value': auth_cookies_dict.get('krb_token', ''),
            'domain': 'your-domain.com',
            'path': '/',
            'secure': True
        },
        {
            'name': 'SESSION_ID',
            'value': auth_cookies_dict.get('session_id', ''),
            'domain': 'your-domain.com', 
            'path': '/',
            'secure': True
        }
    ]
    
    for cookie in cookies_to_add:
        if cookie['value']:
            driver.add_cookie(cookie)
            print(f"Added custom cookie: {cookie['name']}")

if __name__ == "__main__":
    main()
