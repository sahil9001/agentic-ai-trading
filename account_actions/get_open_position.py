"""Get open positions from Binance Futures account."""

from client.binance_client import get_binance_client
from typing import List, Dict


def get_open_position() -> List[Dict[str, str | float]]:
    """
    Get open positions from Binance Futures account.
    
    Returns:
        List of dictionaries with open positions, each containing:
            - symbol: Trading pair symbol (e.g., "ETHUSDT")
            - position: Position size (absolute value)
            - sign: "LONG" or "SHORT"
            - unrealizedPnl: Unrealized profit and loss
            - realizedPnl: Realized profit and loss (from cumulative realized PnL)
            - liquidationPrice: Liquidation price
    """
    client = get_binance_client()
    
    try:
        # Get futures account information which includes positions
        # The futures_account() method returns account info with positions array
        account_info = client.futures_account()
        
        # Extract positions from account info
        positions = account_info.get('positions', [])
        
        open_positions = []
        
        for position in positions:
            position_amt = float(position.get('positionAmt', 0))
            
            # Only include positions with non-zero amount (open positions)
            if position_amt != 0:
                # Determine sign: positive = LONG, negative = SHORT
                sign = "LONG" if position_amt > 0 else "SHORT"
                
                # Get unrealized PnL
                unrealized_pnl = float(position.get('unrealizedProfit', 0))
                
                # Get cumulative realized PnL for this position
                # Note: This is cumulative realized PnL for the symbol, not just this position
                cum_realized_pnl = float(position.get('cumRealizedPnl', 0))
                
                # Get liquidation price
                liquidation_price = float(position.get('liquidationPrice', 0))
                
                open_positions.append({
                    "symbol": position.get('symbol', ''),
                    "position": abs(position_amt),  # Absolute value for position size
                    "sign": sign,
                    "unrealizedPnl": unrealized_pnl,
                    "realizedPnl": cum_realized_pnl,  # Using cumulative realized PnL
                    "liquidationPrice": liquidation_price
                })
        
        return open_positions
        
    except Exception as e:
        raise Exception(f"Failed to get open positions: {str(e)}")

