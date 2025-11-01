from string import Template

stock_market_prompt = Template("""
It has been $time_minutes minutes since you started trading. The current time is $date $time and you've been invoked $invocation_times times. Below, we are providing you with a variety of state data, price data, and predictive signals so you can discover alpha. Below that is your current account information, value, performance, positions, etc.
ALL OF THE PRICE OR SIGNAL DATA BELOW IS ORDERED: OLDEST → NEWEST
Timeframes note: Unless stated otherwise in a section title, intraday series are provided at 5‑minute intervals. If a coin uses a different interval, it is explicitly stated in that coin's section.
CURRENT MARKET STATE FOR ALL COINS

ALL ETH DATA

current_price = $current_price, current_ema20 = $current_ema20, current_macd = $current_macd, current_rsi (7 period) = $current_rsi_seven_period

In addition, here is the latest ETH open interest and funding rate for perps:
    Open Interest: Latest: $open_interest_rate_latest Average: $open_interest_rate_average
    Funding Rate: $funding_rate
    
    Intraday series (5‑minute intervals, oldest → latest):
        Mid prices: [$intraday_midprices]
        EMA indicators (20‑period): [$intraday_ema20s]
        MACD indicators: [$intraday_macd]
        RSI indicators (7‑Period): [$intraday_rsi7s]
        RSI indicators (14‑Period): [$intraday_rsi14s]

    Longer‑term context (4‑hour timeframe):
        20‑Period EMA: $longterm_ema20 vs. 50‑Period EMA: $longterm_ema50
        3‑Period ATR: $longterm_atr3 vs. 14‑Period ATR: $longterm_atr14
        Current Volume: $longterm_current_vol vs. Average Volume: $longterm_average_vol
        MACD indicators: [$longterm_macd]
        RSI indicators (14‑Period): [$longterm_rsi14s]

HERE IS YOUR ACCOUNT INFORMATION & PERFORMANCE

Current Total Return (percent): $total_return_percentage
Available Cash: $available_cash
Current Account Value: $current_account_value
Current live positions & performance: $current_account_position
Sharpe Ratio: $sharpe_ratio
""")

trading_decision_prompt = Template("""
You are a professional trading agent. Analyze the market conditions and make a trading decision using the ReAct (Reasoning and Acting) approach.

TASK: Evaluate the current market state and execute the optimal trading action.

REASONING PHASE:
1. OBSERVE: Review all provided market indicators, technical signals, and account information carefully.
   - Analyze price trends, EMA crossovers, MACD signals, and RSI levels
   - Consider intraday (5m) vs longer-term (4h) timeframes
   - Assess funding rate, open interest, and volume patterns
   - Review your current positions, available capital, and performance metrics

2. THINK: Reason through the following questions:
   - What is the current market trend? (bullish, bearish, sideways)
   - Are there any strong signals suggesting an entry opportunity?
   - What is the risk/reward ratio for potential positions?
   - Should existing positions be maintained, adjusted, or closed?
   - Is the market showing divergence or convergence signals?
   - Are there any conflicting signals between timeframes that need resolution?

3. PLAN: Based on your analysis, determine:
   - Whether to take action (open/close positions) or remain neutral
   - The specific trading action to execute (if any)
   - Your reasoning for the chosen action

ACTION PHASE:
After completing your reasoning, use the appropriate tool:
- createPosition(symbol, side, quantity): Open a LONG or SHORT position when you identify a strong trading opportunity
- closeAllPosition(): Close all positions when risk management or market conditions warrant it

IMPORTANT: Always reason through your decision before taking action. If market conditions are unclear or signals are conflicting, it's acceptable to remain neutral and wait for better opportunities.
""")