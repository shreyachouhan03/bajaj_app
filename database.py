"""
In-memory database for the Trading API SDK
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from models import (
    Instrument, Order, Trade, PortfolioHolding,
    OrderType, OrderStatus, InstrumentType
)


class TradingDatabase:
    """In-memory database for trading data"""
    
    def __init__(self):
        self.instruments: Dict[str, Instrument] = {}
        self.orders: Dict[str, Order] = {}
        self.trades: List[Trade] = []
        self.portfolio: Dict[str, PortfolioHolding] = {}  # Key: f"{symbol}_{exchange}"
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample instruments"""
        sample_instruments = [
            Instrument(
                symbol="RELIANCE",
                exchange="NSE",
                instrumentType=InstrumentType.EQUITY,
                lastTradedPrice=2450.50
            ),
            Instrument(
                symbol="TCS",
                exchange="NSE",
                instrumentType=InstrumentType.EQUITY,
                lastTradedPrice=3450.75
            ),
            Instrument(
                symbol="INFY",
                exchange="NSE",
                instrumentType=InstrumentType.EQUITY,
                lastTradedPrice=1450.25
            ),
            Instrument(
                symbol="HDFCBANK",
                exchange="NSE",
                instrumentType=InstrumentType.EQUITY,
                lastTradedPrice=1650.00
            ),
            Instrument(
                symbol="ICICIBANK",
                exchange="NSE",
                instrumentType=InstrumentType.EQUITY,
                lastTradedPrice=950.50
            ),
            Instrument(
                symbol="BHARTIARTL",
                exchange="NSE",
                instrumentType=InstrumentType.EQUITY,
                lastTradedPrice=1050.00
            ),
            Instrument(
                symbol="SBIN",
                exchange="NSE",
                instrumentType=InstrumentType.EQUITY,
                lastTradedPrice=550.25
            ),
            Instrument(
                symbol="WIPRO",
                exchange="NSE",
                instrumentType=InstrumentType.EQUITY,
                lastTradedPrice=450.75
            ),
        ]
        
        for instrument in sample_instruments:
            key = f"{instrument.symbol}_{instrument.exchange}"
            self.instruments[key] = instrument
    
    def get_all_instruments(self) -> List[Instrument]:
        """Get all available instruments"""
        return list(self.instruments.values())
    
    def get_instrument(self, symbol: str, exchange: str) -> Optional[Instrument]:
        """Get instrument by symbol and exchange"""
        key = f"{symbol}_{exchange}"
        return self.instruments.get(key)
    
    def create_order(self, order: Order) -> Order:
        """Create a new order"""
        self.orders[order.orderId] = order
        return order
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        return self.orders.get(order_id)
    
    def update_order(self, order: Order) -> Order:
        """Update existing order"""
        self.orders[order.orderId] = order
        return order
    
    def get_all_orders(self) -> List[Order]:
        """Get all orders"""
        return list(self.orders.values())
    
    def add_trade(self, trade: Trade) -> Trade:
        """Add a new trade"""
        self.trades.append(trade)
        return trade
    
    def get_all_trades(self) -> List[Trade]:
        """Get all trades"""
        return sorted(self.trades, key=lambda x: x.executedAt, reverse=True)
    
    def get_portfolio_holding(self, symbol: str, exchange: str) -> Optional[PortfolioHolding]:
        """Get portfolio holding for a symbol"""
        key = f"{symbol}_{exchange}"
        return self.portfolio.get(key)
    
    def update_portfolio(self, symbol: str, exchange: str, quantity: int, price: float):
        """Update portfolio holdings"""
        key = f"{symbol}_{exchange}"
        
        if key in self.portfolio:
            holding = self.portfolio[key]
            total_quantity = holding.quantity + quantity
            
            if total_quantity == 0:
                # Remove holding if quantity becomes zero
                del self.portfolio[key]
            else:
                # Update average price and quantity
                total_cost = (holding.quantity * holding.averagePrice) + (quantity * price)
                new_avg_price = total_cost / total_quantity if total_quantity > 0 else 0
                
                # Get current market price
                instrument = self.get_instrument(symbol, exchange)
                current_price = instrument.lastTradedPrice if instrument else price
                
                self.portfolio[key] = PortfolioHolding(
                    symbol=symbol,
                    exchange=exchange,
                    quantity=total_quantity,
                    averagePrice=new_avg_price,
                    currentValue=total_quantity * current_price
                )
        else:
            # Create new holding
            if quantity > 0:
                instrument = self.get_instrument(symbol, exchange)
                current_price = instrument.lastTradedPrice if instrument else price
                
                self.portfolio[key] = PortfolioHolding(
                    symbol=symbol,
                    exchange=exchange,
                    quantity=quantity,
                    averagePrice=price,
                    currentValue=quantity * current_price
                )
    
    def get_all_portfolio_holdings(self) -> List[PortfolioHolding]:
        """Get all portfolio holdings"""
        # Update current values based on latest instrument prices
        for key, holding in self.portfolio.items():
            instrument = self.get_instrument(holding.symbol, holding.exchange)
            if instrument:
                holding.currentValue = holding.quantity * instrument.lastTradedPrice
        
        return list(self.portfolio.values())


# Global database instance
db = TradingDatabase()
