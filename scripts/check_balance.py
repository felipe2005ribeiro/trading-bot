import sys
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.exchange_connector import ExchangeConnector
from config.config import Config
from core.logger import get_logger

# Load environment variables
load_dotenv()

def check_balance():
    print("\n" + "="*50)
    print("VERIFYING BINANCE TESTNET BALANCE")
    print("="*50)
    
    try:
        # Initialize exchange connector
        exchange = ExchangeConnector(Config.BINANCE_TESTNET_API_KEY, Config.BINANCE_TESTNET_API_SECRET, testnet=True)
        
        # Fetch balance
        balance = exchange.get_balance()
        
        print(f"\nConnection Successful!")
        print(f"Total Balance (USDT): ${balance['total'].get('USDT', 0):.2f}")
        print(f"Free Balance (USDT):  ${balance['free'].get('USDT', 0):.2f}")
        print(f"Used Balance (USDT):  ${balance['used'].get('USDT', 0):.2f}")
        
        print("\n" + "="*50)
        
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    check_balance()
