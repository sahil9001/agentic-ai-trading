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


# ---------------- RSI ----------------
def get_rsi(prices: List[float], period: int = 14) -> List[float]:
    """
    Calculate Relative Strength Index (RSI).
    
    RSI is a momentum oscillator that measures the speed and magnitude of 
    price changes. Values range from 0 to 100:
    - RSI > 70: Overbought (potential sell signal)
    - RSI < 30: Oversold (potential buy signal)
    
    :param prices: List of closing prices or mid prices.
    :param period: The number of periods for RSI calculation. Default is 14.
    :return: List of RSI values.
    """
    if len(prices) < period + 1:
        raise ValueError(f"Not enough prices provided. Need at least {period + 1} prices for RSI({period})")
    
    # Calculate price changes
    price_changes = []
    for i in range(1, len(prices)):
        price_changes.append(prices[i] - prices[i-1])
    
    # Separate gains and losses
    gains = [max(change, 0) for change in price_changes]
    losses = [abs(min(change, 0)) for change in price_changes]
    
    # Calculate initial average gain and loss
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    rsi_values = []
    
    # Calculate RSI for each subsequent period
    for i in range(period, len(gains)):
        # Calculate RSI
        if avg_loss == 0:
            rsi = 100  # Avoid division by zero when there are no losses
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        rsi_values.append(round(rsi, 2))
        
        # Update average gain and loss using Wilder's smoothing
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    
    return rsi_values

# ---------------- ATR ----------------
def get_atr(candlesticks: List[Dict[str, float]], period: int = 14) -> List[float]:
    """
    Calculate Average True Range (ATR).
    
    ATR measures market volatility by calculating the average of True Range values.
    True Range is the maximum of:
    1. Current High - Current Low
    2. abs(Current High - Previous Close)
    3. abs(Current Low - Previous Close)
    
    ATR is commonly used for:
    - Setting stop-loss levels (2x ATR, 3x ATR from entry)
    - Position sizing based on volatility
    - Identifying volatile vs quiet markets
    
    :param candlesticks: List of candlesticks with 'high', 'low', 'open', 'close' fields
    :param period: The number of periods for ATR calculation. Default is 14.
    :return: List of ATR values.
    """
    if len(candlesticks) < period + 1:
        raise ValueError(f"Not enough candlesticks provided. Need at least {period + 1} for ATR({period})")
    
    # Calculate True Range for each candlestick
    true_ranges = []
    for i in range(1, len(candlesticks)):
        current = candlesticks[i]
        previous = candlesticks[i-1]
        
        # Calculate three possible ranges
        tr1 = current['high'] - current['low']
        tr2 = abs(current['high'] - previous['close'])
        tr3 = abs(current['low'] - previous['close'])
        
        # True Range is the maximum of the three
        true_range = max(tr1, tr2, tr3)
        true_ranges.append(true_range)
    
    # Calculate ATR using EMA of True Ranges
    atr_values = get_ema(true_ranges, period)
    
    return [round(x, 3) for x in atr_values]


# ---------------- Volume Calculations ----------------
def get_volume_statistics(candlesticks: List[Dict[str, float]], period: int = 20) -> Dict[str, float]:
    """
    Calculate volume statistics: current volume and average volume over a period.
    
    :param candlesticks: List of candlesticks with 'volume' field
    :param period: Number of periods to calculate average volume. Default is 20.
    :return: Dictionary with 'current_volume' and 'average_volume'
    """
    if len(candlesticks) < 1:
        raise ValueError("Need at least 1 candlestick for volume statistics")
    
    # Get volumes
    volumes = [c['volume'] for c in candlesticks]
    
    # Current volume is the last volume
    current_volume = volumes[-1]
    
    # Average volume over the specified period
    if len(candlesticks) < period:
        # If not enough data, use all available
        average_volume = sum(volumes) / len(volumes)
    else:
        # Use last 'period' volumes
        average_volume = sum(volumes[-period:]) / period
    
    return {
        "current_volume": round(current_volume, 3),
        "average_volume": round(average_volume, 3)
    }


# ---------------- Sharpe Ratio ----------------
def calculate_sharpe_ratio(portfolio_values: List[float], risk_free_rate: float = 0.0) -> float:
    """
    Calculate Sharpe Ratio for portfolio performance.
    
    Sharpe Ratio measures risk-adjusted return. It's calculated as:
    Sharpe Ratio = (Mean Portfolio Return - Risk-Free Rate) / Standard Deviation of Returns
    
    General interpretation:
    - < 1: Poor risk-adjusted return
    - 1-2: Good risk-adjusted return
    - 2-3: Very good risk-adjusted return
    - > 3: Excellent risk-adjusted return
    
    :param portfolio_values: List of portfolio values over time
    :param risk_free_rate: Risk-free rate (annualized, as decimal). Default is 0.0
    :return: Sharpe Ratio
    """
    if len(portfolio_values) < 2:
        return 0.0
    
    # Calculate returns
    returns = []
    for i in range(1, len(portfolio_values)):
        if portfolio_values[i-1] == 0:
            # Avoid division by zero
            continue
        return_pct = (portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1]
        returns.append(return_pct)
    
    if len(returns) < 2:
        return 0.0
    
    # Calculate mean return
    mean_return = sum(returns) / len(returns)
    
    # Calculate standard deviation of returns
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    std_dev = variance ** 0.5
    
    # Avoid division by zero
    if std_dev == 0:
        return 0.0
    
    # Calculate Sharpe Ratio
    sharpe_ratio = (mean_return - (risk_free_rate / 252)) / std_dev  # Assuming daily returns
    
    return round(sharpe_ratio, 3)


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
    print("EMA(3):", ema_values)

    macd_values = get_macd(prices)
    print("MACD:", macd_values)
    
    # Note: RSI example would need more data points
    # rsi_values = get_rsi(prices, period=14)
    # print("RSI(14):", rsi_values)
