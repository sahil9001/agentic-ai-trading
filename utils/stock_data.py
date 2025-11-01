from typing import Literal
import time
from client.binance_client import get_binance_client
from binance import KLINE_INTERVAL_12HOUR, Client
from .calculations import get_ema, get_macd, get_mid_prices, get_atr, get_rsi, get_volume_statistics


def get_indicators(
    duration: Literal["5m", "4h"],
    symbol: str = "ETHUSDT"
) -> dict[str, list[float]]:
    """
    Get indicators (mid prices, MACD, EMA20, ATR, RSI, volume) for a crypto symbol.
    
    :param duration: Time interval - "5m" for 5-minute candles or "4h" for 4-hour candles
    :param symbol: Crypto trading pair symbol (default: "ETHUSDT")
    :return: Dictionary with midPrices, macd, ema20s, atr, rsi (last 10 values), 
             current_volume and average_volume (single values)
    """
    # Map duration to Binance interval format
    interval = Client.KLINE_INTERVAL_5MINUTE if duration == "5m" else Client.KLINE_INTERVAL_4HOUR
    candle_limit = 50  
    
    # Fetch klines from Binance using python-binance client
    client = get_binance_client()
    klines_data = client.get_klines(
        symbol=symbol,
        interval=interval,
        limit=candle_limit
    )
    
    # Convert Binance klines format to our format
    # Binance format: [Open time, Open, High, Low, Close, Volume, ...]
    candlesticks = [
        {
            "open": float(candle[1]),
            "high": float(candle[2]),
            "low": float(candle[3]),
            "close": float(candle[4]),
            "volume": float(candle[5])
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
    
    # Calculate ATR (need at least 15 candlesticks with high/low for ATR-14)
    if len(candlesticks) < 15:
        raise ValueError(f"Not enough data points for ATR calculation. Got {len(candlesticks)} candles.")
    
    atr_values = get_atr(candlesticks, period=14)
    
    # Calculate RSI (need at least 15 prices for RSI-14)
    if len(mid_prices) < 15:
        raise ValueError(f"Not enough data points for RSI calculation. Got {len(mid_prices)} candles.")
    
    rsi_values = get_rsi(mid_prices, period=14)
    
    # Calculate volume statistics
    volume_stats = get_volume_statistics(candlesticks, period=20)
    
    # Return last 10 values, rounded to 3 decimals
    return {
        "midPrices": [round(x, 3) for x in mid_prices[-10:]],
        "macd": [round(x, 3) for x in macd[-10:]],
        "ema20s": [round(x, 3) for x in ema20s[-10:]],
        "atr": [round(x, 3) for x in atr_values[-10:]],
        "rsi": [round(x, 2) for x in rsi_values[-10:]],
        "current_volume": volume_stats["current_volume"],
        "average_volume": volume_stats["average_volume"]
    }

