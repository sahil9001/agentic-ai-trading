import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PortfolioChart from './components/PortfolioChart';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

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

  return (
    <div className="App">
      <header className="App-header">
        <h1>Trader AI - Portfolio Dashboard</h1>
        {latestData && (
          <div className="latest-stats">
            <div className="stat-item">
              <span className="stat-label">Total Value:</span>
              <span className="stat-value">${parseFloat(latestData.total).toFixed(2)}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Available:</span>
              <span className="stat-value">${parseFloat(latestData.available).toFixed(2)}</span>
            </div>
          </div>
        )}
      </header>
      
      <main className="App-main">
        {loading && <div className="loading">Loading portfolio data...</div>}
        
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

