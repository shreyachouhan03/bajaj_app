"""
Data models for the Trading API SDK
"""
from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


class OrderType(str, Enum):
    """Order type enumeration"""
    BUY = "BUY"
    SELL = "SELL"


class OrderStyle(str, Enum):
    """Order style enumeration"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class OrderStatus(str, Enum):
    """Order status enumeration"""
    NEW = "NEW"
    PLACED = "PLACED"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"


class InstrumentType(str, Enum):
    """Instrument type enumeration"""
    EQUITY = "EQUITY"
    FUTURES = "FUTURES"
    OPTIONS = "OPTIONS"


# Request/Response Models
class Instrument(BaseModel):
    """Financial instrument model"""
    symbol: str
    exchange: str
    instrumentType: InstrumentType
    lastTradedPrice: float = Field(..., gt=0, description="Last traded price must be positive")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "RELIANCE",
                "exchange": "NSE",
                "instrumentType": "EQUITY",
                "lastTradedPrice": 2450.50
            }
        }


class CreateOrderRequest(BaseModel):
    """Request model for creating a new order"""
    symbol: str = Field(..., description="Trading symbol")
    exchange: str = Field(..., description="Exchange name")
    orderType: OrderType = Field(..., description="BUY or SELL")
    orderStyle: OrderStyle = Field(..., description="MARKET or LIMIT")
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")
    price: Optional[float] = Field(None, gt=0, description="Price (mandatory for LIMIT orders)")

    @validator('price')
    def validate_price_for_limit_order(cls, v, values):
        """Validate that price is provided for LIMIT orders"""
        if values.get('orderStyle') == OrderStyle.LIMIT and (v is None or v <= 0):
            raise ValueError('Price is mandatory for LIMIT orders and must be greater than 0')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "RELIANCE",
                "exchange": "NSE",
                "orderType": "BUY",
                "orderStyle": "LIMIT",
                "quantity": 10,
                "price": 2450.00
            }
        }


class Order(BaseModel):
    """Order model"""
    orderId: str
    symbol: str
    exchange: str
    orderType: OrderType
    orderStyle: OrderStyle
    quantity: int
    price: Optional[float]
    status: OrderStatus
    createdAt: datetime
    executedAt: Optional[datetime] = None
    executedPrice: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "orderId": "ORD123456",
                "symbol": "RELIANCE",
                "exchange": "NSE",
                "orderType": "BUY",
                "orderStyle": "LIMIT",
                "quantity": 10,
                "price": 2450.00,
                "status": "EXECUTED",
                "createdAt": "2024-01-15T10:30:00",
                "executedAt": "2024-01-15T10:30:05",
                "executedPrice": 2449.50
            }
        }


class Trade(BaseModel):
    """Trade model for executed trades"""
    tradeId: str
    orderId: str
    symbol: str
    exchange: str
    orderType: OrderType
    quantity: int
    price: float
    executedAt: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "tradeId": "TRD123456",
                "orderId": "ORD123456",
                "symbol": "RELIANCE",
                "exchange": "NSE",
                "orderType": "BUY",
                "quantity": 10,
                "price": 2449.50,
                "executedAt": "2024-01-15T10:30:05"
            }
        }


class PortfolioHolding(BaseModel):
    """Portfolio holding model"""
    symbol: str
    exchange: str
    quantity: int
    averagePrice: float
    currentValue: float

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "RELIANCE",
                "exchange": "NSE",
                "quantity": 50,
                "averagePrice": 2400.00,
                "currentValue": 122500.00
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    message: str
    statusCode: int

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Price is mandatory for LIMIT orders",
                "statusCode": 400
            }
        }
