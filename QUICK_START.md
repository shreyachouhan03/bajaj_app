# Quick Start Guide - Testing the Trading API

## 🚀 Quick Start (3 Steps)

### Step 1: Start the Server
```bash
python main.py
```

You'll see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 2: Test the API

**Option A: Use Swagger UI (Recommended)**
1. Open browser: `http://localhost:8000/docs`
2. Click any endpoint → "Try it out"
3. Fill in parameters → "Execute"
4. See results!

**Option B: Run Demo Script**
```bash
python demo_api.py
```

**Option C: Use cURL Script**
```bash
./test_api.sh
```

### Step 3: View Logs
```bash
# View real-time logs
tail -f logs/trading_api.log

# Or view all logs
cat logs/trading_api.log
```

---

## 📋 Sample API Calls

### Get All Instruments
```bash
curl -X GET "http://localhost:8000/api/v1/instruments" \
  -H "Authorization: Bearer mock_auth_token_12345"
```

### Place a Buy Order
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

### Get Portfolio
```bash
curl -X GET "http://localhost:8000/api/v1/portfolio" \
  -H "Authorization: Bearer mock_auth_token_12345"
```

---

## 📁 Log Files

All API operations are logged to:
- **File**: `logs/trading_api.log`
- **Format**: Rotating logs (max 10MB, keeps 5 backups)
- **Location**: Automatically created when server starts

**Log includes:**
- API requests
- Order creation and execution
- Portfolio updates
- Errors and exceptions
- All server operations

---

## 🔍 Testing Methods Summary

| Method | Command | Best For |
|--------|---------|----------|
| **Swagger UI** | Open `http://localhost:8000/docs` | Interactive testing |
| **Demo Script** | `python demo_api.py` | Complete workflow demo |
| **cURL Script** | `./test_api.sh` | Command-line testing |
| **Unit Tests** | `pytest test_trading_api.py -v` | Automated testing |

---

## ❓ Troubleshooting

**Server won't start?**
```bash
# Check if port 8000 is free
lsof -i :8000

# Install dependencies
pip install -r requirements.txt
```

**Can't connect?**
- Make sure server is running: `python main.py`
- Check URL: `http://localhost:8000`
- Verify authentication token: `mock_auth_token_12345`

**Want more details?**
- See `TESTING.md` for comprehensive testing guide
- Check logs: `logs/trading_api.log`
- View Swagger docs: `http://localhost:8000/docs`

---

## ✅ What Gets Logged

Every API call logs:
- ✅ Request details (endpoint, parameters)
- ✅ Order creation and status changes
- ✅ Trade execution
- ✅ Portfolio updates
- ✅ Errors and exceptions
- ✅ Authentication attempts

Example log entry:
```
2024-01-15 10:30:00 - __main__ - INFO - User user_12345 placing order: symbol=RELIANCE orderType=BUY quantity=10
2024-01-15 10:30:00 - __main__ - INFO - Order ORD123456 created with status NEW
2024-01-15 10:30:00 - __main__ - INFO - Market order ORD123456 executed at 2450.50
```

---

**Ready to test?** Start the server and visit `http://localhost:8000/docs`! 🚀
