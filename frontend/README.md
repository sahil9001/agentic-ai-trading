# Trader AI Frontend

React frontend application for visualizing portfolio data from the Trader AI trading agent.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Make sure the API server is running on port 8000:
```bash
# From the project root
python api_server.py
```

3. Start the React development server:
```bash
npm start
```

The application will open at `http://localhost:3000`.

## Features

- Real-time portfolio value visualization
- Time-based graph showing total portfolio value over time
- Automatic data refresh every 30 seconds
- Latest portfolio statistics display

## Technologies

- React 18
- Recharts for data visualization
- Axios for API communication

