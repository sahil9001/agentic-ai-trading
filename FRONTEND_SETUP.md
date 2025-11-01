# Frontend Setup Guide

This guide explains how to set up and run the portfolio dashboard frontend.

## Overview

The application consists of:
1. **Database** (`database/models.py`) - SQLite database storing portfolio data with timestamps
2. **API Server** (`api_server.py`) - FastAPI server serving portfolio data
3. **React Frontend** (`frontend/`) - React application with time-based graph visualization

## Setup Instructions

### 1. Install Python Dependencies

Make sure you have the required Python packages:

```bash
# From project root
uv sync
# or
pip install -e .
```

This will install FastAPI, uvicorn, and other dependencies from `pyproject.toml`.

### 2. Start the API Server

The API server must be running before starting the frontend:

```bash
# From project root
python api_server.py
```

The API will be available at `http://localhost:8000`.

### 3. Install Frontend Dependencies

```bash
# From project root
cd frontend
npm install
```

### 4. Start the React Application

```bash
# From frontend directory
npm start
```

The application will open at `http://localhost:3000` automatically.

### 5. Run the Trading Agent

To start collecting portfolio data, run the main trading agent:

```bash
# From project root (in a separate terminal)
python main.py
```

The agent will:
- Run every 5 minutes
- Collect portfolio data
- Save data to the SQLite database (`portfolio.db`)
- The frontend will automatically refresh every 30 seconds to show new data

## API Endpoints

- `GET /api/portfolio/history` - Get all portfolio history (optional `?limit=N` parameter)
- `GET /api/portfolio/latest` - Get the latest portfolio data point

## Database Schema

The `portfolio_history` table stores:
- `id` - Auto-incrementing primary key
- `timestamp` - ISO format timestamp string
- `total` - Total portfolio value (REAL)
- `available` - Available balance (REAL)
- `created_at` - Database insertion timestamp

## Troubleshooting

### Frontend can't connect to API
- Make sure the API server is running on port 8000
- Check that CORS is enabled (it should be by default)

### No data showing
- Make sure the trading agent (`main.py`) has run at least once
- Check that `portfolio.db` exists and contains data
- Verify the API endpoints return data by visiting `http://localhost:8000/api/portfolio/history`

### Port conflicts
- API server: Change port in `api_server.py` (default: 8000)
- Frontend: Set `PORT` environment variable or change in `package.json` (default: 3000)

