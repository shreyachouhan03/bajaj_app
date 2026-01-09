#!/bin/bash

# Trading API Test Script using cURL
# This script demonstrates how to test all API endpoints using cURL commands

BASE_URL="http://localhost:8000"
AUTH_TOKEN="mock_auth_token_12345"

echo "=================================================================="
echo "  TRADING API SDK - cURL TEST SCRIPT"
echo "=================================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print section headers
print_section() {
    echo ""
    echo "------------------------------------------------------------------"
    echo "  $1"
    echo "------------------------------------------------------------------"
}

# Check if server is running
print_section "Checking Server Status"
echo -e "${BLUE}Testing root endpoint...${NC}"
curl -s -X GET "$BASE_URL/" | python3 -m json.tool || echo -e "${RED}Server is not running! Start it with: python main.py${NC}"
echo ""

# Test 1: Get Instruments
print_section "TEST 1: Get All Instruments"
echo -e "${BLUE}GET /api/v1/instruments${NC}"
curl -X GET "$BASE_URL/api/v1/instruments" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool
echo ""

# Test 2: Create Market Buy Order
print_section "TEST 2: Create Market BUY Order"
echo -e "${BLUE}POST /api/v1/orders${NC}"
ORDER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/orders" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "orderType": "BUY",
    "orderStyle": "MARKET",
    "quantity": 10
  }')
echo "$ORDER_RESPONSE" | python3 -m json.tool
ORDER_ID=$(echo "$ORDER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('orderId', ''))" 2>/dev/null)
echo ""

# Test 3: Get Order Status
if [ ! -z "$ORDER_ID" ]; then
    print_section "TEST 3: Get Order Status"
    echo -e "${BLUE}GET /api/v1/orders/$ORDER_ID${NC}"
    curl -X GET "$BASE_URL/api/v1/orders/$ORDER_ID" \
      -H "Authorization: Bearer $AUTH_TOKEN" \
      -H "Content-Type: application/json" | python3 -m json.tool
    echo ""
fi

# Test 4: Create Limit Buy Order
print_section "TEST 4: Create Limit BUY Order"
echo -e "${BLUE}POST /api/v1/orders${NC}"
curl -X POST "$BASE_URL/api/v1/orders" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "TCS",
    "exchange": "NSE",
    "orderType": "BUY",
    "orderStyle": "LIMIT",
    "quantity": 5,
    "price": 3500.00
  }' | python3 -m json.tool
echo ""

# Test 5: Get Trades
print_section "TEST 5: Get All Trades"
echo -e "${BLUE}GET /api/v1/trades${NC}"
curl -X GET "$BASE_URL/api/v1/trades" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool
echo ""

# Test 6: Get Portfolio
print_section "TEST 6: Get Portfolio"
echo -e "${BLUE}GET /api/v1/portfolio${NC}"
curl -X GET "$BASE_URL/api/v1/portfolio" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool
echo ""

# Test 7: Error Handling - Invalid Instrument
print_section "TEST 7: Error Handling - Invalid Instrument"
echo -e "${BLUE}POST /api/v1/orders (with invalid symbol)${NC}"
curl -X POST "$BASE_URL/api/v1/orders" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "INVALID_STOCK",
    "exchange": "NSE",
    "orderType": "BUY",
    "orderStyle": "MARKET",
    "quantity": 10
  }' | python3 -m json.tool
echo ""

# Test 8: Error Handling - Missing Price for LIMIT Order
print_section "TEST 8: Error Handling - Missing Price for LIMIT Order"
echo -e "${BLUE}POST /api/v1/orders (LIMIT without price)${NC}"
curl -X POST "$BASE_URL/api/v1/orders" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "orderType": "BUY",
    "orderStyle": "LIMIT",
    "quantity": 10
  }' | python3 -m json.tool
echo ""

echo "=================================================================="
echo "  All Tests Completed!"
echo "=================================================================="
echo ""
echo "Check logs/trading_api.log for detailed server logs"
echo ""
