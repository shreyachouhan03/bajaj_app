# Testing the Trading API SDK

This guide explains different ways to test the API endpoints of the Trading API SDK.

## Prerequisites

1. Make sure the server is running:
   ```bash
   python main.py
   ```
   
   You should see:
   ```
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```

2. The server will create a `logs/` directory with `trading_api.log` file containing all API logs.

---

## Method 1: Using Swagger UI (Easiest)

**FastAPI automatically generates interactive API documentation!**

1. Start the server:
   ```bash
   python main.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000/docs
   ```

3. Click on any endpoint to expand it
4. Click "Try it out"
5. Fill in the parameters
6. Click "Execute"
7. See the response below

**Benefits:**
- No code required
- Interactive interface
- See request/response schemas
- Test all endpoints easily

---

## Method 2: Using the Demo Python Script

We've created a comprehensive demo script that tests all endpoints.

1. **Install requests library** (if not already installed):
   ```bash
   pip install requests
   ```

2. **Start the server in one terminal:**
   ```bash
   python main.py
   ```

3. **Run the demo script in another terminal:**
   ```bash
   python demo_api.py
   ```

This will:
- Test all API endpoints automatically
- Show formatted responses
- Demonstrate a complete trading workflow
- Test error cases

**Example output:**
```
======================================================================
  TEST 1: Get All Instruments
======================================================================

Fetching all available instruments...
Status Code: 200
Response: [
  {
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "instrumentType": "EQUITY",
    "lastTradedPrice": 2450.5
  },
  ...
]
```

---

## Method 3: Using cURL Commands

We've created a bash script with all cURL commands.

1. **Start the server:**
   ```bash
   python main.py
   ```

2. **Run the test script:**
   ```bash
   ./test_api.sh
   ```

   Or manually run individual cURL commands:

### Get All Instruments
```bash
curl -X GET "http://localhost:8000/api/v1/instruments" \
  -H "Authorization: Bearer mock_auth_token_12345"
```

### Create Market Buy Order
```bash
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Authorization: Bearer mock_auth_token_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "orderType": "BUY",
    "orderStyle": "MARKET",
    "quantity": 10
  }'
```

### Get Order Status
```bash
# Replace ORD12345678 with actual order ID from previous response
curl -X GET "http://localhost:8000/api/v1/orders/ORD12345678" \
  -H "Authorization: Bearer mock_auth_token_12345"
```

### Get All Trades
```bash
curl -X GET "http://localhost:8000/api/v1/trades" \
  -H "Authorization: Bearer mock_auth_token_12345"
```

### Get Portfolio
```bash
curl -X GET "http://localhost:8000/api/v1/portfolio" \
  -H "Authorization: Bearer mock_auth_token_12345"
```

---

## Method 4: Using Postman or Insomnia

1. **Import the API schema:**
   - Visit `http://localhost:8000/openapi.json`
   - Copy the JSON schema
   - Import it into Postman/Insomnia

2. **Set Authorization Header:**
   - Add header: `Authorization: Bearer mock_auth_token_12345`

3. **Test endpoints:**
   - Use the imported collection
   - Modify request bodies as needed
   - Execute requests

---

## Method 5: Using Python requests (Manual)

Create your own test script:

```python
import requests
import json

BASE_URL = "http://localhost:8000"
HEADERS = {
    "Authorization": "Bearer mock_auth_token_12345",
    "Content-Type": "application/json"
}

# Get instruments
response = requests.get(f"{BASE_URL}/api/v1/instruments", headers=HEADERS)
print("Instruments:", json.dumps(response.json(), indent=2))

# Create order
order_data = {
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "orderType": "BUY",
    "orderStyle": "MARKET",
    "quantity": 10
}
response = requests.post(f"{BASE_URL}/api/v1/orders", headers=HEADERS, json=order_data)
order = response.json()
print("Order Created:", json.dumps(order, indent=2))

# Get order status
order_id = order["orderId"]
response = requests.get(f"{BASE_URL}/api/v1/orders/{order_id}", headers=HEADERS)
print("Order Status:", json.dumps(response.json(), indent=2))
```

---

## Complete Testing Workflow Example

Here's a recommended workflow to test everything:

### Step 1: Start the Server
```bash
python main.py
```

### Step 2: Check Server is Running
```bash
curl http://localhost:8000/
```

### Step 3: View Available Instruments
```bash
curl -X GET "http://localhost:8000/api/v1/instruments" \
  -H "Authorization: Bearer mock_auth_token_12345" | python3 -m json.tool
```

### Step 4: Place a Buy Order
```bash
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Authorization: Bearer mock_auth_token_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "orderType": "BUY",
    "orderStyle": "MARKET",
    "quantity": 10
  }' | python3 -m json.tool
```

**Save the orderId from the response!**

### Step 5: Check Order Status
```bash
# Replace ORDER_ID with the orderId from Step 4
curl -X GET "http://localhost:8000/api/v1/orders/ORDER_ID" \
  -H "Authorization: Bearer mock_auth_token_12345" | python3 -m json.tool
```

### Step 6: View Executed Trades
```bash
curl -X GET "http://localhost:8000/api/v1/trades" \
  -H "Authorization: Bearer mock_auth_token_12345" | python3 -m json.tool
```

### Step 7: View Portfolio
```bash
curl -X GET "http://localhost:8000/api/v1/portfolio" \
  -H "Authorization: Bearer mock_auth_token_12345" | python3 -m json.tool
```

### Step 8: Place a Sell Order (if you have holdings)
```bash
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Authorization: Bearer mock_auth_token_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "orderType": "SELL",
    "orderStyle": "MARKET",
    "quantity": 5
  }' | python3 -m json.tool
```

---

## Testing Error Cases

### Test 1: Invalid Instrument
```bash
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Authorization: Bearer mock_auth_token_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "INVALID_STOCK",
    "exchange": "NSE",
    "orderType": "BUY",
    "orderStyle": "MARKET",
    "quantity": 10
  }'
```

**Expected:** 404 Not Found

### Test 2: Missing Price for LIMIT Order
```bash
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Authorization: Bearer mock_auth_token_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "orderType": "BUY",
    "orderStyle": "LIMIT",
    "quantity": 10
  }'
```

**Expected:** 422 Validation Error

### Test 3: Insufficient Holdings for Sell
```bash
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Authorization: Bearer mock_auth_token_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "orderType": "SELL",
    "orderStyle": "MARKET",
    "quantity": 10000
  }'
```

**Expected:** 400 Bad Request - Insufficient holdings

### Test 4: Unauthorized Access
```bash
curl -X GET "http://localhost:8000/api/v1/instruments"
```

**Expected:** 401 Unauthorized

---

## Viewing Logs

All API requests and operations are logged to:
```
logs/trading_api.log
```

**View logs in real-time:**
```bash
tail -f logs/trading_api.log
```

**View recent logs:**
```bash
cat logs/trading_api.log
```

**Search logs:**
```bash
grep "Order" logs/trading_api.log
grep "ERROR" logs/trading_api.log
```

---

## Running Unit Tests

Run the comprehensive unit test suite:

```bash
pytest test_trading_api.py -v
```

This will test all endpoints programmatically.

---

## Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/v1/instruments` | GET | Get all instruments |
| `/api/v1/orders` | POST | Create new order |
| `/api/v1/orders/{orderId}` | GET | Get order status |
| `/api/v1/trades` | GET | Get all trades |
| `/api/v1/portfolio` | GET | Get portfolio holdings |

**Authentication:** All endpoints (except `/`) require:
```
Authorization: Bearer mock_auth_token_12345
```

**Swagger UI:** `http://localhost:8000/docs`

---

## Troubleshooting

### Server won't start
- Check if port 8000 is already in use
- Make sure all dependencies are installed: `pip install -r requirements.txt`

### Connection refused
- Make sure the server is running
- Check the URL is correct: `http://localhost:8000`

### 401 Unauthorized
- Check the Authorization header is included
- Verify the token is correct: `mock_auth_token_12345`

### 404 Not Found
- Check the endpoint URL is correct
- For order status, verify the orderId exists

---

## Need Help?

- Check the Swagger UI at `http://localhost:8000/docs` for interactive testing
- View logs at `logs/trading_api.log`
- Run the demo script: `python demo_api.py`
