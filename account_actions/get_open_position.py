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
        open_positions = client.futures_position_information()
        return open_positions
        
    except Exception as e:
        raise Exception(f"Failed to get open positions: {str(e)}")

