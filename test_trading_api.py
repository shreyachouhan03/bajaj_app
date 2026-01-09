"""
Unit tests for Trading API SDK
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from database import TradingDatabase
from models import OrderType, OrderStyle, OrderStatus

# Test client
client = TestClient(app)

# Mock auth token
MOCK_AUTH_TOKEN = "mock_auth_token_12345"
AUTH_HEADERS = {"Authorization": f"Bearer {MOCK_AUTH_TOKEN}"}


class TestInstrumentsAPI:
    """Test cases for Instruments API"""
    
    def test_get_instruments_success(self):
        """Test successful retrieval of instruments"""
        response = client.get("/api/v1/instruments", headers=AUTH_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "symbol" in data[0]
        assert "exchange" in data[0]
        assert "instrumentType" in data[0]
        assert "lastTradedPrice" in data[0]
    
    def test_get_instruments_unauthorized(self):
        """Test unauthorized access to instruments"""
        response = client.get("/api/v1/instruments")
        assert response.status_code == 401


class TestOrdersAPI:
    """Test cases for Orders API"""
    
    def test_create_market_buy_order_success(self):
        """Test successful creation of market buy order"""
        order_data = {
            "symbol": "RELIANCE",
            "exchange": "NSE",
            "orderType": "BUY",
            "orderStyle": "MARKET",
            "quantity": 10
        }
        response = client.post("/api/v1/orders", json=order_data, headers=AUTH_HEADERS)
        assert response.status_code == 201
        data = response.json()
        assert "orderId" in data
        assert data["symbol"] == "RELIANCE"
        assert data["orderType"] == "BUY"
        assert data["orderStyle"] == "MARKET"
        assert data["quantity"] == 10
        assert data["status"] in ["PLACED", "EXECUTED"]
    
    def test_create_limit_buy_order_success(self):
        """Test successful creation of limit buy order"""
        order_data = {
            "symbol": "TCS",
            "exchange": "NSE",
            "orderType": "BUY",
            "orderStyle": "LIMIT",
            "quantity": 5,
            "price": 3500.00
        }
        response = client.post("/api/v1/orders", json=order_data, headers=AUTH_HEADERS)
        assert response.status_code == 201
        data = response.json()
        assert data["orderStyle"] == "LIMIT"
        assert data["price"] == 3500.00
    
    def test_create_order_missing_price_for_limit(self):
        """Test validation error when price is missing for LIMIT order"""
        order_data = {
            "symbol": "RELIANCE",
            "exchange": "NSE",
            "orderType": "BUY",
            "orderStyle": "LIMIT",
            "quantity": 10
        }
        response = client.post("/api/v1/orders", json=order_data, headers=AUTH_HEADERS)
        assert response.status_code == 422  # Validation error
    
    def test_create_order_invalid_quantity(self):
        """Test validation error for invalid quantity"""
        order_data = {
            "symbol": "RELIANCE",
            "exchange": "NSE",
            "orderType": "BUY",
            "orderStyle": "MARKET",
            "quantity": 0
        }
        response = client.post("/api/v1/orders", json=order_data, headers=AUTH_HEADERS)
        assert response.status_code == 422
    
    def test_create_order_instrument_not_found(self):
        """Test error when instrument doesn't exist"""
        order_data = {
            "symbol": "INVALID",
            "exchange": "NSE",
            "orderType": "BUY",
            "orderStyle": "MARKET",
            "quantity": 10
        }
        response = client.post("/api/v1/orders", json=order_data, headers=AUTH_HEADERS)
        assert response.status_code == 404
    
    def test_create_sell_order_insufficient_holdings(self):
        """Test error when trying to sell more than available holdings"""
        order_data = {
            "symbol": "RELIANCE",
            "exchange": "NSE",
            "orderType": "SELL",
            "orderStyle": "MARKET",
            "quantity": 1000  # More than available
        }
        response = client.post("/api/v1/orders", json=order_data, headers=AUTH_HEADERS)
        assert response.status_code == 400
    
    def test_get_order_status_success(self):
        """Test successful retrieval of order status"""
        # First create an order
        order_data = {
            "symbol": "INFY",
            "exchange": "NSE",
            "orderType": "BUY",
            "orderStyle": "MARKET",
            "quantity": 2
        }
        create_response = client.post("/api/v1/orders", json=order_data, headers=AUTH_HEADERS)
        order_id = create_response.json()["orderId"]
        
        # Then get order status
        response = client.get(f"/api/v1/orders/{order_id}", headers=AUTH_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["orderId"] == order_id
        assert "status" in data
        assert data["status"] in ["NEW", "PLACED", "EXECUTED", "CANCELLED"]
    
    def test_get_order_status_not_found(self):
        """Test error when order doesn't exist"""
        response = client.get("/api/v1/orders/INVALID_ORDER", headers=AUTH_HEADERS)
        assert response.status_code == 404


class TestTradesAPI:
    """Test cases for Trades API"""
    
    def test_get_trades_success(self):
        """Test successful retrieval of trades"""
        # Create and execute an order first
        order_data = {
            "symbol": "HDFCBANK",
            "exchange": "NSE",
            "orderType": "BUY",
            "orderStyle": "MARKET",
            "quantity": 3
        }
        client.post("/api/v1/orders", json=order_data, headers=AUTH_HEADERS)
        
        # Get trades
        response = client.get("/api/v1/trades", headers=AUTH_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "tradeId" in data[0]
            assert "orderId" in data[0]
            assert "symbol" in data[0]
            assert "price" in data[0]


class TestPortfolioAPI:
    """Test cases for Portfolio API"""
    
    def test_get_portfolio_success(self):
        """Test successful retrieval of portfolio"""
        # Create a buy order to add to portfolio
        order_data = {
            "symbol": "ICICIBANK",
            "exchange": "NSE",
            "orderType": "BUY",
            "orderStyle": "MARKET",
            "quantity": 5
        }
        client.post("/api/v1/orders", json=order_data, headers=AUTH_HEADERS)
        
        # Get portfolio
        response = client.get("/api/v1/portfolio", headers=AUTH_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Portfolio may be empty or have holdings
        if len(data) > 0:
            assert "symbol" in data[0]
            assert "quantity" in data[0]
            assert "averagePrice" in data[0]
            assert "currentValue" in data[0]


class TestRootEndpoint:
    """Test cases for root endpoint"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
