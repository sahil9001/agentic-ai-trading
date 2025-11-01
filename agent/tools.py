"""Tool definitions for the agent."""

from langchain.tools import tool
from typing import Dict, Callable, Literal
from account_actions.create_order import create_position
from account_actions.close_order import close_order


@tool
def createPosition(symbol: str, side: Literal["LONG", "SHORT"], quantity: float) -> str:
    """Open a position in the given market.

    Args:
        symbol: The symbol to open the position at (e.g., "ETH/USDT")
        side: "LONG" or "SHORT"
        quantity: The quantity of the position to open
    
    Returns:
        Success message
    """
    try:
        # Convert symbol format from "ETH/USDT" to "ETHUSDT" for Binance
        binance_symbol = symbol.replace("/", "")
        create_position(binance_symbol, side, quantity)
        return f"Position opened successfully for {quantity} {symbol}"
    except Exception as e:
        return f"Failed to open position: {str(e)}"


@tool
def closeAllPosition() -> str:
    """Close all the currently open positions.

    Returns:
        Success message
    """
    try:
        results = close_order()
        if len(results) == 1 and "message" in results[0]:
            return results[0]["message"]
        return f"All positions closed successfully. Closed {len(results)} position(s)."
    except Exception as e:
        return f"Failed to close positions: {str(e)}"


def get_tools():
    """Get all available tools.
    
    Returns:
        List of tool instances
    """
    return [createPosition, closeAllPosition]


def get_tools_by_name() -> Dict[str, Callable]:
    """Get tools organized by name for quick lookup.
    
    Returns:
        Dictionary mapping tool names to tool instances
    """
    tools = get_tools()
    return {tool.name: tool for tool in tools}

