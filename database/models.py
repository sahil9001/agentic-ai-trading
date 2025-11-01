"""Database models and schema for portfolio tracking."""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import os


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "portfolio.db")


def init_database():
    """Initialize the database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolio_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            total REAL NOT NULL,
            available REAL NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create index on timestamp for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp 
        ON portfolio_history(timestamp)
    """)
    
    conn.commit()
    conn.close()


def save_portfolio_data(total: float, available: float, timestamp: Optional[str] = None):
    """
    Save portfolio data to the database.
    
    Args:
        total: Total portfolio value
        available: Available balance
        timestamp: Optional timestamp string. If None, uses current time.
    """
    if timestamp is None:
        timestamp = datetime.utcnow().isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO portfolio_history (timestamp, total, available)
        VALUES (?, ?, ?)
    """, (timestamp, float(total), float(available)))
    
    conn.commit()
    conn.close()


def get_portfolio_history(limit: Optional[int] = None) -> List[Dict[str, any]]:
    """
    Retrieve portfolio history from the database.
    
    Args:
        limit: Optional limit on number of records to return
    
    Returns:
        List of dictionaries with timestamp, total, and available
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if limit:
        cursor.execute("""
            SELECT timestamp, total, available
            FROM portfolio_history
            ORDER BY timestamp ASC
            LIMIT ?
        """, (limit,))
    else:
        cursor.execute("""
            SELECT timestamp, total, available
            FROM portfolio_history
            ORDER BY timestamp ASC
        """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


# Initialize database on module import
init_database()

