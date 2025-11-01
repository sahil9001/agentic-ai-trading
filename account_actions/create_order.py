"""Create a futures order on Binance."""

import time
from typing import Literal
from client.binance_client import get_binance_client


def create_position(symbol: str, side: Literal["LONG", "SHORT"], quantity: float) -> dict:
    """
    Create a futures position order on Binance.
    
    Args:
        symbol: Trading pair symbol (e.g., "ETHUSDT")
        side: "LONG" for buy, "SHORT" for sell
        quantity: Order quantity (amount of base asset)
    
    Returns:
        Dictionary containing the order response from Binance
    
    Raises:
        Exception: If no latest price found or order creation fails
    """
    client = get_binance_client()
    
    try:
        # Get latest price from 1-minute candlesticks (last 5 minutes)
        # Similar to the JS code which gets last 5 minutes of 1m candles
        end_time = int(time.time() * 1000)  # Current time in milliseconds
        start_time = end_time - (5 * 60 * 1000)  # 5 minutes ago
        
        klines_data = client.futures_klines(
            symbol=symbol,
            interval="1m",
            startTime=start_time,
            endTime=end_time,
            limit=5
        )
        
        if not klines_data or len(klines_data) == 0:
            raise Exception("No candlestick data found")
        
        # Get the latest close price (last candle)
        # Binance klines format: [Open time, Open, High, Low, Close, Volume, ...]
        latest_price = float(klines_data[-1][4])  # Close price is at index 4
        
        if not latest_price or latest_price <= 0:
            raise Exception("No latest price found")
        
        # Determine order side: BUY for LONG, SELL for SHORT
        order_side = "BUY" if side == "LONG" else "SELL"
        
        # Create market order on Binance Futures
        # Note: Market orders execute immediately at current market price
        # The JS code uses a price adjustment (1.01x for LONG, 0.99x for SHORT),
        # but for simplicity we use MARKET order type which doesn't require price
        response = client.futures_create_order(
            symbol=symbol,
            side=order_side,
            type="MARKET",
            quantity=quantity
        )
        
        return response
        
    except Exception as e:
        raise Exception(f"Failed to create position: {str(e)}")

