"""Main entry point for the trader-ai application."""

import time
from utils.stock_data import get_indicators
from utils.calculations import get_ema, get_atr, get_rsi, get_macd, get_mid_prices, calculate_sharpe_ratio
from prompts.trading_prompt import stock_market_prompt, trading_decision_prompt
from account_actions.get_portfolio import get_portfolio
from account_actions.get_open_position import get_open_position
from agent.builder import build_agent
from database.models import save_portfolio_data, get_portfolio_history
from datetime import datetime
from client.binance_client import get_binance_client
from binance import Client

# Track invocation count across all calls
invocation_count = 0
# Track start time for calculating elapsed minutes
start_time = time.time()
# Initial account value (from the old prompt, user was given $5000)
INITIAL_ACCOUNT_VALUE = 5000.0


def invoke_agent():
    """Main function to invoke the trading agent."""
    global invocation_count
    
    # Increment invocation count
    invocation_count += 1
    
    # Market configuration
    symbol = "ETHUSDT"
    
    # Get intraday indicators (5m)
    intraday_indicators = get_indicators("5m", symbol)
    
    # Get long-term indicators (4h)
    longterm_indicators = get_indicators("4h", symbol)
    
    # Get client for additional data
    client = get_binance_client()
    
    # Get raw klines data for additional calculations
    intraday_klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_5MINUTE, limit=50)
    longterm_klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_4HOUR, limit=50)
    
    # Convert to candlestick format
    intraday_candlesticks = [
        {
            "open": float(candle[1]),
            "high": float(candle[2]),
            "low": float(candle[3]),
            "close": float(candle[4]),
            "volume": float(candle[5])
        }
        for candle in intraday_klines
    ]
    
    longterm_candlesticks = [
        {
            "open": float(candle[1]),
            "high": float(candle[2]),
            "low": float(candle[3]),
            "close": float(candle[4]),
            "volume": float(candle[5])
        }
        for candle in longterm_klines
    ]
    
    # Calculate additional intraday indicators
    intraday_mid_prices = get_mid_prices(intraday_candlesticks)
    intraday_rsi7 = get_rsi(intraday_mid_prices, period=7)
    intraday_rsi14 = get_rsi(intraday_mid_prices, period=14)
    
    # Calculate additional long-term indicators
    longterm_mid_prices = get_mid_prices(longterm_candlesticks)
    longterm_ema50 = get_ema(longterm_mid_prices, 50)
    longterm_atr3 = get_atr(longterm_candlesticks, period=3)
    longterm_atr14 = get_atr(longterm_candlesticks, period=14)
    longterm_rsi14 = get_rsi(longterm_mid_prices, period=14)
    longterm_macd = get_macd(longterm_mid_prices)
    
    # Get current values (latest values)
    current_price = intraday_mid_prices[-1] if intraday_mid_prices else 0
    current_ema20 = intraday_indicators["ema20s"][-1] if intraday_indicators["ema20s"] else 0
    current_macd = intraday_indicators["macd"][-1] if intraday_indicators["macd"] else 0
    current_rsi_seven_period = intraday_rsi7[-1] if intraday_rsi7 else 0
    
    # Get open interest and funding rate
    try:
        open_interest_data = client.futures_open_interest(symbol=symbol)
        open_interest_latest = float(open_interest_data.get('openInterest', 0))
        
        # Get historical open interest for average (last 24 hours)
        # Note: Binance API may have limits, using latest as fallback
        open_interest_rate_average = open_interest_latest  # Simplified - could be improved
    except Exception as e:
        print(f"Warning: Failed to get open interest: {e}")
        open_interest_latest = 0
        open_interest_rate_average = 0
    
    try:
        funding_rate_data = client.futures_funding_rate(symbol=symbol, limit=1)
        funding_rate = float(funding_rate_data[0].get('fundingRate', 0)) if funding_rate_data else 0
    except Exception as e:
        print(f"Warning: Failed to get funding rate: {e}")
        funding_rate = 0
    
    # Get portfolio information
    portfolio = get_portfolio()
    
    # Save portfolio data to database
    try:
        save_portfolio_data(
            total=float(portfolio['total']),
            available=float(portfolio['available']),
            timestamp=datetime.utcnow().isoformat()
        )
        print(f"Portfolio data saved to database: Total=${portfolio['total']}, Available=${portfolio['available']}")
    except Exception as e:
        print(f"Warning: Failed to save portfolio data to database: {e}")
    
    # Get open positions
    try:
        open_positions_list = get_open_position()
        print(open_positions_list)
        if not open_positions_list:
            current_account_position = "No open positions"
        else:
            # Filter positions with non-zero amounts and format them
            filtered_positions = [
                pos for pos in open_positions_list 
                if float(pos.get('positionAmt', 0)) != 0
            ]
            if filtered_positions:
                current_account_position = ", ".join([
                    f"{pos.get('symbol', 'N/A')} {pos.get('positionAmt', 'N/A')} {pos.get('positionSide', 'N/A')}" 
                    for pos in filtered_positions
                ])
            else:
                current_account_position = "No open positions"
    except Exception as e:
        print(f"Warning: Failed to get open positions: {e}")
        current_account_position = "No open positions"
        open_positions_list = []
    
    # Calculate total return percentage
    current_account_value = float(portfolio['total'])
    total_return_percentage = ((current_account_value - INITIAL_ACCOUNT_VALUE) / INITIAL_ACCOUNT_VALUE) * 100
    
    # Calculate Sharpe Ratio from portfolio history
    try:
        portfolio_history = get_portfolio_history()
        if len(portfolio_history) >= 2:
            portfolio_values = [entry['total'] for entry in portfolio_history]
            sharpe_ratio = calculate_sharpe_ratio(portfolio_values)
        else:
            sharpe_ratio = 0.0
    except Exception as e:
        print(f"Warning: Failed to calculate Sharpe ratio: {e}")
        sharpe_ratio = 0.0
    
    # Calculate elapsed time in minutes
    global start_time
    elapsed_minutes = int((time.time() - start_time) / 60)
    
    # Get current date and time
    now = datetime.now()
    current_date = now.strftime('%Y-%m-%d')
    current_time = now.strftime('%H:%M:%S')
    
    # Prepare enriched prompt using stock_market_prompt
    enriched_prompt = stock_market_prompt.substitute(
        time_minutes=str(elapsed_minutes),
        date=current_date,
        time=current_time,
        invocation_times=str(invocation_count),
        current_price=f"{current_price:.3f}",
        current_ema20=f"{current_ema20:.3f}",
        current_macd=f"{current_macd:.3f}",
        current_rsi_seven_period=f"{current_rsi_seven_period:.2f}",
        open_interest_rate_latest=f"{open_interest_latest:.2f}",
        open_interest_rate_average=f"{open_interest_rate_average:.2f}",
        funding_rate=f"{funding_rate:.6f}",
        intraday_midprices=",".join(str(x) for x in intraday_indicators["midPrices"][-10:]),
        intraday_ema20s=",".join(str(x) for x in intraday_indicators["ema20s"][-10:]),
        intraday_macd=",".join(str(x) for x in intraday_indicators["macd"][-10:]),
        intraday_rsi7s=",".join(str(x) for x in intraday_rsi7[-10:]),
        intraday_rsi14s=",".join(str(x) for x in intraday_rsi14[-10:]),
        longterm_ema20=f"{longterm_indicators['ema20s'][-1]:.3f}" if longterm_indicators["ema20s"] else "0",
        longterm_ema50=f"{longterm_ema50[-1]:.3f}" if longterm_ema50 else "0",
        longterm_atr3=f"{longterm_atr3[-1]:.3f}" if longterm_atr3 else "0",
        longterm_atr14=f"{longterm_atr14[-1]:.3f}" if longterm_atr14 else "0",
        longterm_current_vol=f"{longterm_indicators['current_volume']:.3f}",
        longterm_average_vol=f"{longterm_indicators['average_volume']:.3f}",
        longterm_macd=",".join(str(x) for x in longterm_macd[-10:]),
        longterm_rsi14s=",".join(str(x) for x in longterm_rsi14[-10:]),
        total_return_percentage=f"{total_return_percentage:.2f}",
        sharpe_ratio=f"{sharpe_ratio:.3f}",
        available_cash=f"${portfolio['available']}",
        current_account_value=f"${portfolio['total']}",
        current_account_position=current_account_position
    )
    
    print("=" * 80)
    print("ENRICHED PROMPT FOR AGENT:")
    print("=" * 80)
    print(enriched_prompt)
    print("=" * 80)
    print("\nInvoking agent...\n")
    
    # Build and invoke agent
    agent = build_agent(temperature=0, system_prompt=enriched_prompt)
    
    # Invoke agent with a ReAct-style prompt to trigger trading decision
    user_message = trading_decision_prompt.substitute()
    response = agent.invoke({
        "messages": [("user", user_message)]
    })
    
    print("=" * 80)
    print("AGENT RESPONSE:")
    print("=" * 80)
    # Extract the messages from the response
    messages = response.get("messages", [])
    for msg in messages:
        print(f"{msg.__class__.__name__}: {msg.content}")
    print("=" * 80)
    
    return response


def main():
    """Run the trading agent in a loop every 5 minutes."""
    print("Starting trader-ai agent...")
    print("Will run every 5 minutes.")
    print("Press Ctrl+C to stop.\n")
    
    while True:
        try:
            print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running agent invocation...")
            invoke_agent()
            print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Waiting 5 minutes until next invocation...\n")
            time.sleep(60 * 5)  # Wait 5 minutes
        except KeyboardInterrupt:
            print("\n\nAgent stopped by user.")
            break
        except Exception as e:
            print(f"\nError during agent invocation: {e}")
            print("Waiting 5 minutes before retry...\n")
            time.sleep(60 * 5)


if __name__ == "__main__":
    main()
