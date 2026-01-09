"""
Trading API SDK - Main FastAPI Application
"""
import os
import uuid
import logging
from datetime import datetime
from typing import List
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from models import (
    Instrument, CreateOrderRequest, Order, Trade, PortfolioHolding,
    OrderType, OrderStatus, OrderStyle
)
from database import db
from exceptions import (
    TradingAPIException, InstrumentNotFoundError, OrderNotFoundError,
    InvalidOrderError, InsufficientHoldingError
)

# Configure logging to both console and file

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure root logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# File handler with rotation (max 10MB, keep 5 backup files)
file_handler = RotatingFileHandler(
    'logs/trading_api.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)


# Mock authentication - single hardcoded user
MOCK_USER_ID = "user_12345"
MOCK_AUTH_TOKEN = "mock_auth_token_12345"


def verify_auth(authorization: str = Header(None)):
    """Mock authentication - verify authorization header"""
    if authorization is None or authorization != f"Bearer {MOCK_AUTH_TOKEN}":
        raise HTTPException(
            status_code=401,
            detail="Unauthorized. Please provide valid authorization token."
        )
    return MOCK_USER_ID


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    logger.info("Starting Trading API SDK...")
    logger.info(f"Initialized with {len(db.get_all_instruments())} instruments")
    yield
    logger.info("Shutting down Trading API SDK...")


# Initialize FastAPI app
app = FastAPI(
    title="Trading API SDK",
    description="A simplified Trading API SDK for stock broking operations",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(TradingAPIException)
async def trading_api_exception_handler(request, exc: TradingAPIException):
    """Centralized exception handler for Trading API exceptions"""
    logger.error(f"Trading API Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.detail,
            "statusCode": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Global exception handler for unexpected errors"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "statusCode": 500
        }
    )


def simulate_order_execution(order: Order, instrument: Instrument) -> Order:
    """
    Simulate order execution logic
    - MARKET orders: Execute immediately at last traded price (with small variation)
    - LIMIT orders: Execute if price is favorable
    """
    import random
    
    if order.orderStyle == OrderStyle.MARKET:
        # Market orders execute immediately with small price variation
        price_variation = random.uniform(-0.1, 0.1)  # ±0.1% variation
        executed_price = instrument.lastTradedPrice * (1 + price_variation)
        executed_price = round(executed_price, 2)
        
        order.status = OrderStatus.EXECUTED
        order.executedAt = datetime.now()
        order.executedPrice = executed_price
        
        logger.info(f"Market order {order.orderId} executed at {executed_price}")
        
    elif order.orderStyle == OrderStyle.LIMIT:
        # Limit orders execute if price is favorable
        if order.orderType == OrderType.BUY:
            # Buy limit: execute if limit price >= market price
            if order.price and order.price >= instrument.lastTradedPrice:
                executed_price = min(order.price, instrument.lastTradedPrice * 1.001)
                executed_price = round(executed_price, 2)
                
                order.status = OrderStatus.EXECUTED
                order.executedAt = datetime.now()
                order.executedPrice = executed_price
                
                logger.info(f"Buy limit order {order.orderId} executed at {executed_price}")
            else:
                # Keep as PLACED, will be executed later if price moves
                order.status = OrderStatus.PLACED
                logger.info(f"Buy limit order {order.orderId} placed at {order.price} (market: {instrument.lastTradedPrice})")
        
        elif order.orderType == OrderType.SELL:
            # Sell limit: execute if limit price <= market price
            if order.price and order.price <= instrument.lastTradedPrice:
                executed_price = max(order.price, instrument.lastTradedPrice * 0.999)
                executed_price = round(executed_price, 2)
                
                order.status = OrderStatus.EXECUTED
                order.executedAt = datetime.now()
                order.executedPrice = executed_price
                
                logger.info(f"Sell limit order {order.orderId} executed at {executed_price}")
            else:
                # Keep as PLACED
                order.status = OrderStatus.PLACED
                logger.info(f"Sell limit order {order.orderId} placed at {order.price} (market: {instrument.lastTradedPrice})")
    
    return order


# API Endpoints

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "message": "Trading API SDK",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/v1/instruments", response_model=List[Instrument], tags=["Instruments"])
async def get_instruments(user_id: str = Depends(verify_auth)):
    """
    Fetch list of tradable instruments
    
    Returns all available financial instruments with their details including
    symbol, exchange, instrument type, and last traded price.
    """
    logger.info(f"User {user_id} requested instruments list")
    instruments = db.get_all_instruments()
    return instruments


@app.post("/api/v1/orders", response_model=Order, status_code=201, tags=["Orders"])
async def create_order(
    order_request: CreateOrderRequest,
    user_id: str = Depends(verify_auth)
):
    """
    Place a new order
    
    Creates a new buy or sell order with MARKET or LIMIT style.
    - Quantity must be greater than 0
    - Price is mandatory for LIMIT orders
    - Validates instrument availability
    - For SELL orders, validates sufficient holdings
    """
    logger.info(f"User {user_id} placing order: {order_request}")
    
    # Validate instrument exists
    instrument = db.get_instrument(order_request.symbol, order_request.exchange)
    if not instrument:
        raise InstrumentNotFoundError(order_request.symbol, order_request.exchange)
    
    # For SELL orders, check if user has sufficient holdings
    if order_request.orderType == OrderType.SELL:
        holding = db.get_portfolio_holding(order_request.symbol, order_request.exchange)
        available_quantity = holding.quantity if holding else 0
        
        if available_quantity < order_request.quantity:
            raise InsufficientHoldingError(
                order_request.symbol,
                available_quantity,
                order_request.quantity
            )
    
    # Create order
    order_id = f"ORD{uuid.uuid4().hex[:8].upper()}"
    order = Order(
        orderId=order_id,
        symbol=order_request.symbol,
        exchange=order_request.exchange,
        orderType=order_request.orderType,
        orderStyle=order_request.orderStyle,
        quantity=order_request.quantity,
        price=order_request.price,
        status=OrderStatus.NEW,
        createdAt=datetime.now()
    )
    
    # Save order
    db.create_order(order)
    logger.info(f"Order {order_id} created with status NEW")
    
    # Simulate order placement and execution
    order.status = OrderStatus.PLACED
    db.update_order(order)
    logger.info(f"Order {order_id} status updated to PLACED")
    
    # Execute order if conditions are met
    order = simulate_order_execution(order, instrument)
    db.update_order(order)
    
    # If order is executed, create trade and update portfolio
    if order.status == OrderStatus.EXECUTED and order.executedPrice:
        # Create trade
        trade_id = f"TRD{uuid.uuid4().hex[:8].upper()}"
        trade = Trade(
            tradeId=trade_id,
            orderId=order.orderId,
            symbol=order.symbol,
            exchange=order.exchange,
            orderType=order.orderType,
            quantity=order.quantity,
            price=order.executedPrice,
            executedAt=order.executedAt or datetime.now()
        )
        db.add_trade(trade)
        logger.info(f"Trade {trade_id} created for order {order_id}")
        
        # Update portfolio
        portfolio_quantity = order.quantity if order.orderType == OrderType.BUY else -order.quantity
        db.update_portfolio(
            order.symbol,
            order.exchange,
            portfolio_quantity,
            order.executedPrice
        )
        logger.info(f"Portfolio updated for {order.symbol}")
    
    return order


@app.get("/api/v1/orders/{order_id}", response_model=Order, tags=["Orders"])
async def get_order_status(order_id: str, user_id: str = Depends(verify_auth)):
    """
    Fetch order status
    
    Returns the current status and details of an order by its ID.
    Supported order states: NEW, PLACED, EXECUTED, CANCELLED
    """
    logger.info(f"User {user_id} requested status for order {order_id}")
    
    order = db.get_order(order_id)
    if not order:
        raise OrderNotFoundError(order_id)
    
    return order


@app.get("/api/v1/trades", response_model=List[Trade], tags=["Trades"])
async def get_trades(user_id: str = Depends(verify_auth)):
    """
    Fetch list of executed trades
    
    Returns all executed trades for the authenticated user,
    sorted by execution time (most recent first).
    """
    logger.info(f"User {user_id} requested trades list")
    trades = db.get_all_trades()
    return trades


@app.get("/api/v1/portfolio", response_model=List[PortfolioHolding], tags=["Portfolio"])
async def get_portfolio(user_id: str = Depends(verify_auth)):
    """
    Fetch current portfolio holdings
    
    Returns all current portfolio holdings with:
    - Symbol and exchange
    - Quantity held
    - Average purchase price
    - Current market value
    """
    logger.info(f"User {user_id} requested portfolio")
    holdings = db.get_all_portfolio_holdings()
    return holdings


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
