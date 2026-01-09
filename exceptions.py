"""
Custom exceptions for the Trading API SDK
"""
from fastapi import HTTPException, status


class TradingAPIException(HTTPException):
    """Base exception for Trading API"""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=message)


class InstrumentNotFoundError(TradingAPIException):
    """Exception raised when instrument is not found"""
    def __init__(self, symbol: str, exchange: str):
        message = f"Instrument {symbol} not found on {exchange}"
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class OrderNotFoundError(TradingAPIException):
    """Exception raised when order is not found"""
    def __init__(self, order_id: str):
        message = f"Order {order_id} not found"
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class InvalidOrderError(TradingAPIException):
    """Exception raised for invalid order operations"""
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)


class InsufficientHoldingError(TradingAPIException):
    """Exception raised when trying to sell more than available holdings"""
    def __init__(self, symbol: str, available: int, requested: int):
        message = f"Insufficient holdings for {symbol}. Available: {available}, Requested: {requested}"
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)
