"""
Demo script to test Trading API endpoints
This script demonstrates how to use all the API endpoints
"""
import requests
import json
import time
from typing import Dict, Any

# API Configuration
BASE_URL = "http://localhost:8000"
AUTH_TOKEN = "mock_auth_token_12345"
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def print_response(response: requests.Response, description: str = ""):
    """Print formatted API response"""
    if description:
        print(f"{description}")
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, default=str)}")
    except:
        print(f"Response: {response.text}")
    print("-" * 70)


def test_get_instruments():
    """Test GET /api/v1/instruments"""
    print_section("TEST 1: Get All Instruments")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/instruments", headers=HEADERS)
        print_response(response, "Fetching all available instruments...")
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the API. Make sure the server is running!")
        print("Run: python main.py")
        return None


def test_create_market_buy_order(symbol: str = "RELIANCE", quantity: int = 10):
    """Test POST /api/v1/orders - Market Buy Order"""
    print_section(f"TEST 2: Create Market BUY Order - {symbol}")
    
    order_data = {
        "symbol": symbol,
        "exchange": "NSE",
        "orderType": "BUY",
        "orderStyle": "MARKET",
        "quantity": quantity
    }
    
    print(f"Order Data: {json.dumps(order_data, indent=2)}")
    print("\nPlacing order...")
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/orders", headers=HEADERS, json=order_data)
        print_response(response, f"Creating market BUY order for {quantity} shares of {symbol}...")
        return response.json() if response.status_code == 201 else None
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the API. Make sure the server is running!")
        return None


def test_create_limit_buy_order(symbol: str = "TCS", quantity: int = 5, price: float = 3500.00):
    """Test POST /api/v1/orders - Limit Buy Order"""
    print_section(f"TEST 3: Create Limit BUY Order - {symbol}")
    
    order_data = {
        "symbol": symbol,
        "exchange": "NSE",
        "orderType": "BUY",
        "orderStyle": "LIMIT",
        "quantity": quantity,
        "price": price
    }
    
    print(f"Order Data: {json.dumps(order_data, indent=2)}")
    print("\nPlacing order...")
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/orders", headers=HEADERS, json=order_data)
        print_response(response, f"Creating limit BUY order for {quantity} shares of {symbol} at ₹{price}...")
        return response.json() if response.status_code == 201 else None
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the API. Make sure the server is running!")
        return None


def test_get_order_status(order_id: str):
    """Test GET /api/v1/orders/{orderId}"""
    print_section(f"TEST 4: Get Order Status - {order_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/orders/{order_id}", headers=HEADERS)
        print_response(response, f"Fetching status for order {order_id}...")
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the API. Make sure the server is running!")
        return None


def test_get_trades():
    """Test GET /api/v1/trades"""
    print_section("TEST 5: Get All Executed Trades")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/trades", headers=HEADERS)
        print_response(response, "Fetching all executed trades...")
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the API. Make sure the server is running!")
        return None


def test_get_portfolio():
    """Test GET /api/v1/portfolio"""
    print_section("TEST 6: Get Portfolio Holdings")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/portfolio", headers=HEADERS)
        print_response(response, "Fetching portfolio holdings...")
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the API. Make sure the server is running!")
        return None


def test_create_sell_order(symbol: str = "RELIANCE", quantity: int = 5):
    """Test POST /api/v1/orders - Sell Order"""
    print_section(f"TEST 7: Create SELL Order - {symbol}")
    
    order_data = {
        "symbol": symbol,
        "exchange": "NSE",
        "orderType": "SELL",
        "orderStyle": "MARKET",
        "quantity": quantity
    }
    
    print(f"Order Data: {json.dumps(order_data, indent=2)}")
    print("\nPlacing order...")
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/orders", headers=HEADERS, json=order_data)
        print_response(response, f"Creating market SELL order for {quantity} shares of {symbol}...")
        return response.json() if response.status_code == 201 else None
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the API. Make sure the server is running!")
        return None


def test_error_cases():
    """Test error handling"""
    print_section("TEST 8: Error Handling Examples")
    
    # Test 1: Invalid instrument
    print("\n8.1 Testing with invalid instrument...")
    order_data = {
        "symbol": "INVALID_STOCK",
        "exchange": "NSE",
        "orderType": "BUY",
        "orderStyle": "MARKET",
        "quantity": 10
    }
    try:
        response = requests.post(f"{BASE_URL}/api/v1/orders", headers=HEADERS, json=order_data)
        print_response(response)
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the API.")
    
    # Test 2: Missing price for LIMIT order
    print("\n8.2 Testing LIMIT order without price (should fail)...")
    order_data = {
        "symbol": "RELIANCE",
        "exchange": "NSE",
        "orderType": "BUY",
        "orderStyle": "LIMIT",
        "quantity": 10
        # Missing price field
    }
    try:
        response = requests.post(f"{BASE_URL}/api/v1/orders", headers=HEADERS, json=order_data)
        print_response(response)
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the API.")
    
    # Test 3: Invalid order ID
    print("\n8.3 Testing with invalid order ID...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/orders/INVALID_ORDER_ID", headers=HEADERS)
        print_response(response)
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the API.")


def run_complete_demo():
    """Run complete API demo workflow"""
    print("\n" + "█"*70)
    print(" " * 15 + "TRADING API SDK - DEMO")
    print("█"*70)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
        print(f"\n✓ Server is running at {BASE_URL}")
    except requests.exceptions.ConnectionError:
        print(f"\n✗ ERROR: Server is not running at {BASE_URL}")
        print("  Please start the server first:")
        print("  > python main.py")
        return
    except requests.exceptions.Timeout:
        print(f"\n✗ ERROR: Server timeout. Is it running at {BASE_URL}?")
        return
    
    # Run all tests
    instruments = test_get_instruments()
    time.sleep(1)
    
    order1 = test_create_market_buy_order("RELIANCE", 10)
    time.sleep(1)
    
    order2 = test_create_limit_buy_order("TCS", 5, 3500.00)
    time.sleep(1)
    
    if order1:
        test_get_order_status(order1.get("orderId", ""))
        time.sleep(1)
    
    trades = test_get_trades()
    time.sleep(1)
    
    portfolio = test_get_portfolio()
    time.sleep(1)
    
    if portfolio and len(portfolio) > 0:
        # Try to sell some holdings
        first_holding = portfolio[0]
        if first_holding.get("quantity", 0) > 0:
            test_create_sell_order(first_holding["symbol"], min(5, first_holding["quantity"]))
            time.sleep(1)
    
    test_error_cases()
    
    # Final portfolio check
    print_section("FINAL: Updated Portfolio After All Trades")
    test_get_portfolio()
    
    print("\n" + "█"*70)
    print(" " * 20 + "DEMO COMPLETED!")
    print("█"*70 + "\n")
    print("Check the logs in 'logs/trading_api.log' for detailed server logs.\n")


if __name__ == "__main__":
    print("\nStarting Trading API Demo...")
    print("Make sure the server is running: python main.py\n")
    time.sleep(2)
    run_complete_demo()
