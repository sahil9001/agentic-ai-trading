"""Main entry point for the trader-ai application."""

import time
from utils.stock_data import get_indicators
from prompts.trading_prompt import agent_prompt, indicator_prompt
from account_actions.get_portfolio import get_portfolio
from account_actions.get_open_position import get_open_position
from agent.builder import build_agent
from database.models import save_portfolio_data
from datetime import datetime

# Track invocation count across all calls
invocation_count = 0


def invoke_agent():
    """Main function to invoke the trading agent."""
    global invocation_count
    
    # Increment invocation count
    invocation_count += 1
    
    # Market configuration
    MARKETS = {
        "ETH/USDT": {"marketId": "ETHUSDT"}
    }
    
    # Fetch indicators for all markets
    all_indicator_data = ""
    
    for market_slug, market_info in MARKETS.items():
        # Get intraday indicators (5m)
        intraday_indicators = get_indicators("5m", market_info["marketId"])
        
        # Get long-term indicators (4h)
        longterm_indicators = get_indicators("4h", market_info["marketId"])
        
        # Format the indicator data using the template
        indicator_data = indicator_prompt.substitute(
            marketSlug=market_slug,
            intraday_midprices=",".join(str(x) for x in intraday_indicators["midPrices"]),
            intraday_ema20s=",".join(str(x) for x in intraday_indicators["ema20s"]),
            intraday_macd=",".join(str(x) for x in intraday_indicators["macd"]),
            longterm_midprices=",".join(str(x) for x in longterm_indicators["midPrices"]),
            longterm_ema20s=",".join(str(x) for x in longterm_indicators["ema20s"]),
            longterm_macd=",".join(str(x) for x in longterm_indicators["macd"])
        )
        
        all_indicator_data += indicator_data + "\n"
    
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
            open_positions_str = ""
        else:
            open_positions_str = ", ".join([
                f"{pos['symbol']} {pos['position']} {pos['sign']}" 
                for pos in open_positions_list
            ])
    except Exception as e:
        print(f"Warning: Failed to get open positions: {e}")
        open_positions_str = ""
    
    # Prepare enriched prompt
    enriched_prompt = agent_prompt.substitute(
        invocation_times=str(invocation_count),
        open_positions=open_positions_str if open_positions_str else "None",
        portfolio_value=f"${portfolio['total']}",
        all_indicator_data=all_indicator_data,
        available_cash=f"${portfolio['available']}",
        current_account_value=f"${portfolio['total']}",
        current_account_position=open_positions_list if open_positions_list else "No open positions"
    )
    
    print("=" * 80)
    print("ENRICHED PROMPT FOR AGENT:")
    print("=" * 80)
    print(enriched_prompt)
    print("=" * 80)
    print("\nInvoking agent...\n")
    
    # Build and invoke agent
    agent = build_agent(temperature=0, system_prompt=enriched_prompt)
    
    # Invoke agent with a simple message to trigger trading decision
    response = agent.invoke({
        "messages": [("user", "Based on the current market conditions and indicators, make a trading decision. You can either create a position using the createPosition tool or close existing positions using the closeAllPosition tool.")]
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
