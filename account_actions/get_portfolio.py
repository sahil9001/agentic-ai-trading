"""Get portfolio information from Binance account."""

from client.binance_client import get_binance_client


def get_portfolio() -> dict[str, str]:
    """
    Get portfolio information from Binance Futures account.
    
    Returns:
        Dict with:
            - total: Total portfolio value in USDT (string)
            - available: Available balance in USDT (string)
    
    Raises:
        Exception: If API authentication fails or account data cannot be retrieved.
        Provides detailed guidance for common API key permission issues.
    """
    client = get_binance_client()
    
    # First, verify the client connection works (test public endpoint)
    try:
        client.ping()
    except Exception as conn_error:
        raise Exception(f"Failed to connect to Binance API: {str(conn_error)}")
    
    # Try futures account first (since other functions use futures)
    futures_error = None
    try:
        account_info = client.futures_account()
        # Extract wallet balance and available balance from futures account
        total_wallet_balance = float(account_info.get('totalWalletBalance', 0))
        available_balance = float(account_info.get('availableBalance', 0))
        
        return {
            'total': str(total_wallet_balance),
            'available': str(available_balance)
        }
    except Exception as e:
        futures_error = e
        # If futures account access fails, raise the error with helpful message
        raise Exception(f"Failed to access Binance Futures account: {str(futures_error)}")