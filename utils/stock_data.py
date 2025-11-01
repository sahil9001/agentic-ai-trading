from typing import Literal
import time
from client.binance_client import get_binance_client
from .calculations import get_ema, get_macd, get_mid_prices


def get_indicators(
    duration: Literal["5m", "4h"],
    symbol: str = "ETHUSDT"
) -> dict[str, list[float]]:
    """
    Get indicators (mid prices, MACD, EMA20) for a crypto symbol.
    
    :param duration: Time interval - "5m" for 5-minute candles or "4h" for 4-hour candles
    :param symbol: Crypto trading pair symbol (default: "ETHUSDT")
    :return: Dictionary with midPrices, macd, and ema20s (last 10 values each, rounded to 3 decimals)
    """
    # Map duration to Binance interval format
    interval = duration  # Binance supports "5m" and "4h" directly
    
    # Calculate time range
    # For 5m: need at least 26 candles for MACD, so ~2.5 hours (30 candles = 150 minutes)
    # For 4h: need at least 26 candles for MACD, so ~104 hours (26 candles = 104 hours)
    hours_back = 3 if duration == "5m" else 104
    start_time = int((time.time() - (hours_back * 60 * 60)) * 1000)  # Convert to milliseconds
    limit = 100  # Request up to 100 candles to ensure we have enough data
    
    # Fetch klines from Binance using python-binance client
    client = get_binance_client()
    klines_data = client.get_klines(
        symbol=symbol,
        interval=interval,
        startTime=start_time,
        limit=limit
    )
    
    # Convert Binance klines format to our format
    # Binance format: [Open time, Open, High, Low, Close, Volume, ...]
    candlesticks = [
        {
            "open": float(candle[1]),
            "close": float(candle[4])
        }
        for candle in klines_data
    ]
    
    # Calculate mid prices
    mid_prices = get_mid_prices(candlesticks)
    
    # Calculate MACD (need at least 26 prices for MACD)
    if len(mid_prices) < 24:
        raise ValueError(f"Not enough data points for MACD calculation. Got {len(mid_prices)} candles.")
    
    macd = get_macd(mid_prices)
    
    # Calculate EMA20
    if len(mid_prices) < 20:
        raise ValueError(f"Not enough data points for EMA20 calculation. Got {len(mid_prices)} candles.")
    
    ema20s = get_ema(mid_prices, 20)
    
    # Return last 10 values, rounded to 3 decimals
    return {
        "midPrices": [round(x, 3) for x in mid_prices[-10:]],
        "macd": [round(x, 3) for x in macd[-10:]],
        "ema20s": [round(x, 3) for x in ema20s[-10:]]
    }

