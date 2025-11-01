"""Close all open futures positions on Binance."""

from client.binance_client import get_binance_client
from typing import List, Dict


def close_order() -> List[Dict]:
    """
    Close all open positions on Binance Futures.
    
    This function:
    1. Retrieves all open positions
    2. For each open position, places an opposite market order to close it
       - LONG positions are closed with a SELL order
       - SHORT positions are closed with a BUY order
    
    Returns:
        List of dictionaries containing close order responses, each with:
            - symbol: Trading pair symbol that was closed
            - response: Order response from Binance API
    
    Raises:
        Exception: If positions cannot be retrieved or orders cannot be created
    """
    client = get_binance_client()
    
    try:
        # Get futures account information to retrieve open positions
        account_info = client.futures_account()
        
        # Extract positions from account info
        positions = account_info.get('positions', [])
        
        close_responses = []
        
        for position in positions:
            position_amt = float(position.get('positionAmt', 0))
            
            # Only process positions with non-zero amount (open positions)
            if position_amt != 0:
                symbol = position.get('symbol', '')
                
                # Determine opposite side to close position:
                # LONG (positive) -> SELL to close
                # SHORT (negative) -> BUY to close
                close_side = "SELL" if position_amt > 0 else "BUY"
                quantity = abs(position_amt)  # Use absolute value for quantity
                
                # Create market order to close the position
                response = client.futures_create_order(
                    symbol=symbol,
                    side=close_side,
                    type="MARKET",
                    quantity=quantity,
                    reduceOnly=True  # Ensures this order only reduces the position
                )
                
                close_responses.append({
                    "symbol": symbol,
                    "response": response
                })
        
        # If no open positions were found
        if len(close_responses) == 0:
            return [{"message": "No open positions to close"}]
        
        return close_responses
        
    except Exception as e:
        raise Exception(f"Failed to close positions: {str(e)}")

