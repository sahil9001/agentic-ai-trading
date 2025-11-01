"""Binance API client initialization and management."""
import os
from binance import Client
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Initialize Binance client (API keys optional for public endpoints like klines)
# API keys can help with rate limits
_api_key = os.getenv("BINANCE_API_KEY")
_api_secret = os.getenv("BINANCE_SECRET_KEY")
# Check if testnet should be used (default to True/testnet - change to False for mainnet)
_use_testnet = os.getenv("BINANCE_TESTNET", "true").lower() == "true"
_client = None


def reset_client():
    """Reset the client singleton (useful for testing or config changes)."""
    global _client
    _client = None


def get_binance_client() -> Client:
    """
    Get or create Binance client instance (singleton pattern).
    
    The client is initialized with API keys if available in environment variables.
    If keys are not provided, a client without authentication is created,
    which can still be used for public endpoints like klines.
    
    Testnet mode can be controlled via BINANCE_TESTNET environment variable:
    - Set BINANCE_TESTNET=true or omit to use Binance testnet (default)
    - Set BINANCE_TESTNET=false to use Binance mainnet
    
    Returns:
        Client: Binance API client instance
    """
    global _client, _use_testnet
    # Re-read testnet setting in case it changed (default to True/testnet)
    _use_testnet = os.getenv("BINANCE_TESTNET", "true").lower() == "true"
    
    if _client is None:
        if _api_key and _api_secret:
            _client = Client(_api_key, _api_secret, testnet=_use_testnet)
        else:
            # Can still use client without keys for public endpoints
            _client = Client(testnet=_use_testnet)
    return _client

