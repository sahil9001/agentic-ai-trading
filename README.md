# Trader AI

An autonomous AI-powered cryptocurrency trading agent that uses technical indicators and AI decision-making to execute trades on Binance Futures. The system features a React dashboard for portfolio tracking and provides real-time market analysis with LangChain agents.

## Features

- **AI Trading Agent**: Uses OpenAI GPT-5-mini to make trading decisions based on technical indicators
- **Technical Analysis**: Calculates EMA20, MACD, and mid-price indicators from 5-minute and 4-hour candlesticks
- **Automated Trading**: Creates and closes leveraged positions on Binance Futures (ETH/USDT with 10x leverage)
- **Portfolio Tracking**: SQLite database stores historical portfolio data with timestamps
- **Real-time Dashboard**: React frontend with interactive charts showing portfolio performance over time
- **API Server**: FastAPI backend serving portfolio data to the frontend
- **Risk Management**: Configurable leverage, position limits, and margin requirements

## Architecture

The application consists of several key components:

1. **Trading Agent** (`main.py`): Main orchestration that runs every 5 minutes, fetches market data, and invokes the AI agent
2. **Agent** (`agent/`): LangChain-based agent with tools for creating and closing positions
3. **API Client** (`client/`): Binance API integration for market data and order execution
4. **Account Actions** (`account_actions/`): Functions for portfolio queries, order creation, and position management
5. **Database** (`database/`): SQLite storage for portfolio history
6. **Frontend** (`frontend/`): React dashboard with portfolio visualization
7. **API Server** (`api_server.py`): FastAPI server exposing portfolio data endpoints

## Prerequisites

- Python 3.10 or higher
- Node.js and npm (for frontend)
- Binance account with API keys
- OpenAI API key

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd trader-ai
```

### 2. Install Python dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Binance Configuration (required for trading)
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET_KEY=your_binance_secret_key_here

# Testnet Mode (set to false for mainnet trading)
BINANCE_TESTNET=true
```

**⚠️ Important**: The system uses Binance testnet by default. Set `BINANCE_TESTNET=false` to trade on mainnet with real funds.

### 4. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

## Usage

### Running the Trading Agent

Start the main trading agent to begin automated trading:

```bash
python main.py
```

The agent will:
- Run every 5 minutes
- Fetch market indicators (EMA20, MACD, mid-prices) for ETH/USDT
- Make trading decisions based on AI analysis
- Save portfolio snapshots to the database
- Display trading activity and decisions in the console

### Running the API Server

Start the FastAPI server to serve portfolio data:

```bash
python api_server.py
```

The API will be available at `http://localhost:8000`

Available endpoints:
- `GET /api/portfolio/history` - Get all portfolio history
- `GET /api/portfolio/history?limit=N` - Get last N data points
- `GET /api/portfolio/latest` - Get the latest portfolio snapshot

### Running the Frontend Dashboard

Start the React development server:

```bash
cd frontend
npm start
```

The dashboard will open at `http://localhost:3000` and automatically refresh every 30 seconds to show new portfolio data.

### Complete Setup

For full functionality, run all three components in separate terminals:

**Terminal 1** - Trading Agent:
```bash
python main.py
```

**Terminal 2** - API Server:
```bash
python api_server.py
```

**Terminal 3** - Frontend:
```bash
cd frontend && npm start
```

## How It Works

### Trading Logic

1. **Market Data Collection**: The agent fetches candlestick data for ETH/USDT on 5-minute and 4-hour timeframes
2. **Indicator Calculation**: Computes EMA20, MACD, and mid-prices for both timeframes
3. **Portfolio Analysis**: Retrieves current portfolio value, available balance, and open positions
4. **AI Decision Making**: The OpenAI agent analyzes indicators and decides whether to:
   - Open a new LONG position
   - Open a new SHORT position
   - Close existing positions
   - Hold and wait
5. **Order Execution**: If a trade is decided, executes market orders on Binance Futures
6. **Data Persistence**: Saves portfolio snapshot to SQLite database

### Technical Indicators

- **EMA20**: 20-period Exponential Moving Average for trend identification
- **MACD**: Moving Average Convergence Divergence for momentum analysis
- **Mid-Prices**: Average of open and close prices for each candle

### Tools Available to Agent

- `createPosition(symbol, side, quantity)`: Open a leveraged position (LONG or SHORT)
- `closeAllPosition()`: Close all open positions at once

## Project Structure

```
trader-ai/
├── account_actions/      # Trading operations and account queries
│   ├── create_order.py   # Open positions
│   ├── close_order.py    # Close positions
│   ├── get_portfolio.py  # Portfolio balance
│   └── get_open_position.py # Open positions info
├── agent/                # AI agent configuration
│   ├── builder.py        # Agent construction
│   ├── tools.py          # Trading tools for agent
│   ├── nodes.py          # State management nodes
│   ├── edges.py          # Agent graph edges
│   └── state.py          # Agent state definition
├── client/               # Exchange integration
│   └── binance_client.py # Binance API client
├── database/             # Data persistence
│   └── models.py         # Database models and queries
├── frontend/             # React dashboard
│   ├── src/
│   │   ├── App.js        # Main app component
│   │   └── components/
│   │       └── PortfolioChart.js
│   └── package.json
├── llm/                  # LLM configuration
│   └── model.py          # OpenAI model setup
├── prompts/              # AI prompts
│   └── trading_prompt.py # Trading agent prompt template
├── utils/                # Utilities
│   ├── stock_data.py     # Market data fetching
│   └── calculations.py   # Technical indicator calculations
├── api_server.py         # FastAPI backend
├── main.py              # Main trading agent entry point
├── pyproject.toml       # Python dependencies
└── README.md            # This file
```

## Configuration

### Leverage and Risk

Current settings in `main.py`:
- Market: ETH/USDT
- Leverage: 10x
- Timeframes: 5m (intraday) and 4h (long-term)
- Invocation interval: 5 minutes

### Agent Behavior

The agent is instructed to:
- Maximize returns while managing risk
- Not risk all capital in any single trade
- Use appropriate position sizing
- Only open one position at a time
- Close positions when opportunities arise

## Testing

Test scripts are provided to verify functionality:

```bash
# Test Binance API connection and data fetching
python test_binance.py

# Test portfolio retrieval
python test_portfolio.py

# Test order creation (dry run)
python test_create_order.py

# Test position queries
python test_open_position.py
```

## Troubleshooting

### Agent Not Making Trades

- Verify API keys are set correctly in `.env`
- Check that `BINANCE_TESTNET` is set appropriately
- Ensure sufficient balance for initial margin
- Review console output for agent decisions and reasoning

### Frontend Shows No Data

- Verify API server is running on port 8000
- Check that `portfolio.db` exists and contains data
- Run `main.py` at least once to generate portfolio snapshots
- Test API endpoints directly: `curl http://localhost:8000/api/portfolio/history`

### Connection Errors

- Ensure Binance API keys have futures trading permissions
- Check network connectivity
- Verify testnet vs mainnet settings match your keys
- Review Binance API status page

## Database Schema

```sql
CREATE TABLE portfolio_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    total REAL NOT NULL,
    available REAL NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## Safety and Risk Warnings

⚠️ **IMPORTANT DISCLAIMERS**:

1. **Use at Your Own Risk**: This is experimental software. Automated trading carries significant financial risk.
2. **Test First**: Always use testnet before deploying to mainnet with real funds.
3. **No Guarantees**: Past performance does not guarantee future results.
4. **Leverage Risk**: Using leverage amplifies both gains and losses.
5. **API Security**: Never commit your `.env` file with real API keys to version control.
6. **Regulatory Compliance**: Ensure your use complies with local regulations and exchange terms of service.

## License

This project is provided as-is for educational and research purposes.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support

For questions or issues, please open an issue on the repository.

