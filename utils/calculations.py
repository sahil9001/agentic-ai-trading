from typing import List, Dict

# ---------------- EMA Calculation ----------------
def get_ema(prices: List[float], period: int) -> List[float]:
    """
    Calculate Exponential Moving Average (EMA).
    :param prices: List of price values.
    :param period: The number of periods for EMA.
    :return: List of EMA values.
    """
    multiplier = 2 / (period + 1)
    
    if len(prices) < period:
        raise ValueError("Not enough prices provided")

    # Initial SMA (Simple Moving Average)
    sma = sum(prices[:period]) / period
    emas = [sma]

    # Calculate EMA for the rest of the prices
    for price in prices[period:]:
        prev_ema = emas[-1]
        ema = prev_ema * (1 - multiplier) + price * multiplier
        emas.append(ema)

    return emas


# ---------------- Mid Prices ----------------
def get_mid_prices(candlesticks: List[Dict[str, float]]) -> List[float]:
    """
    Calculate mid prices for candlesticks.
    Each candlestick should have 'open' and 'close' fields.
    """
    return [round((c['open'] + c['close']) / 2, 3) for c in candlesticks]


# ---------------- MACD ----------------
def get_macd(prices: List[float]) -> List[float]:
    """
    Calculate MACD line using EMA12 and EMA26.
    :param prices: List of mid prices or closing prices.
    :return: List of MACD values.
    """
    ema26 = get_ema(prices, 26)
    ema12 = get_ema(prices, 12)

    # Align both EMAs to the same length
    ema12 = ema12[-len(ema26):]

    # Compute MACD
    macd = [ema12[i] - ema26[i] for i in range(len(ema26))]
    return macd


# ---------------- Example ----------------
if __name__ == "__main__":
    # Example candlestick data
    sample_candles = [
        {"open": 100, "close": 102},
        {"open": 102, "close": 101},
        {"open": 101, "close": 103},
        {"open": 103, "close": 104},
        {"open": 104, "close": 106},
        {"open": 106, "close": 107},
        {"open": 107, "close": 108},
        {"open": 108, "close": 110},
    ]

    prices = get_mid_prices(sample_candles)
    print("Mid Prices:", prices)

    ema_values = get_ema(prices, 3)
    print("EMA:", ema_values)

    macd_values = get_macd(prices)
    print("MACD:", macd_values)
