import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PortfolioChart from './components/PortfolioChart';
import './App.css';

// Use relative URLs in production (nginx handles routing)
// In development, use localhost for the API
const getApiBaseUrl = () => {
  // If explicitly set, use it (can be empty string for relative URLs)
  if (process.env.REACT_APP_API_URL !== undefined) {
    return process.env.REACT_APP_API_URL;
  }
  // In production build, use relative URLs (empty string)
  // In development, use localhost
  return process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

function App() {
  const [portfolioData, setPortfolioData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [latestData, setLatestData] = useState(null);

  const fetchPortfolioData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get(`${API_BASE_URL}/api/portfolio/history`);
      setPortfolioData(response.data);
      
      // Fetch latest data separately
      const latestResponse = await axios.get(`${API_BASE_URL}/api/portfolio/latest`);
      setLatestData(latestResponse.data);
    } catch (err) {
      setError('Failed to fetch portfolio data. Make sure the API server is running on port 8000.');
      console.error('Error fetching portfolio data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolioData();
    
    // Refresh data every 30 seconds
    const interval = setInterval(fetchPortfolioData, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const BASE_VALUE = 5000;
  
  const calculateStats = () => {
    if (!latestData) return null;
    
    const total = parseFloat(latestData.total);
    const change = total - BASE_VALUE;
    const percentChange = ((change / BASE_VALUE) * 100).toFixed(2);
    const isProfit = change >= 0;
    
    return {
      total,
      change,
      percentChange,
      isProfit
    };
  };

  const stats = calculateStats();

  return (
    <div className="App">
      <header className="App-header">
        <h1>Trader AI</h1>
        {stats && (
          <div className="latest-stats">
            <div className="stat-item">
              <span className="stat-label">Current Value</span>
              <span className={`stat-value ${stats.isProfit ? 'profit' : stats.change < 0 ? 'loss' : 'neutral'}`}>
                ${stats.total.toFixed(2)}
              </span>
              <span className={`stat-change ${stats.isProfit ? 'profit' : 'loss'}`}>
                {stats.isProfit ? '+' : ''}{stats.change.toFixed(2)} ({stats.isProfit ? '+' : ''}{stats.percentChange}%)
              </span>
            </div>
          </div>
        )}
      </header>
      
      <main className="App-main">
        {loading && <div className="loading">Loading...</div>}
        
        {error && (
          <div className="error">
            {error}
            <button onClick={fetchPortfolioData} className="retry-button">
              Retry
            </button>
          </div>
        )}
        
        {!loading && !error && portfolioData.length === 0 && (
          <div className="empty-state">
            <p>No portfolio data available yet.</p>
            <p>Start the trading agent to begin collecting data.</p>
          </div>
        )}
        
        {!loading && !error && portfolioData.length > 0 && (
          <PortfolioChart data={portfolioData} />
        )}
      </main>
    </div>
  );
}

export default App;

