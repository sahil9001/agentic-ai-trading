import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const PortfolioChart = ({ data }) => {
  // Format data for the chart
  const chartData = data.map(item => ({
    time: new Date(item.timestamp).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }),
    timestamp: item.timestamp,
    total: parseFloat(item.total),
    available: parseFloat(item.available)
  }));

  // Custom tooltip formatter
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip" style={{
          backgroundColor: 'white',
          padding: '10px',
          border: '1px solid #ccc',
          borderRadius: '5px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
        }}>
          <p style={{ margin: '0 0 5px 0', fontWeight: 'bold' }}>{`${label}`}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ margin: '2px 0', color: entry.color }}>
              {`${entry.name}: $${entry.value.toFixed(2)}`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="chart-container" style={{
      background: 'white',
      padding: '30px',
      borderRadius: '15px',
      boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
      marginTop: '20px'
    }}>
      <h2 style={{ marginBottom: '20px', color: '#333', textAlign: 'center' }}>
        Portfolio Value Over Time
      </h2>
      <ResponsiveContainer width="100%" height={500}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 60 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis
            dataKey="time"
            angle={-45}
            textAnchor="end"
            height={100}
            stroke="#666"
            interval="preserveStartEnd"
          />
          <YAxis
            stroke="#666"
            tickFormatter={(value) => `$${value.toFixed(0)}`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Line
            type="monotone"
            dataKey="total"
            stroke="#667eea"
            strokeWidth={3}
            dot={{ r: 4 }}
            activeDot={{ r: 7 }}
            name="Total Portfolio Value"
          />
          <Line
            type="monotone"
            dataKey="available"
            stroke="#48bb78"
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 6 }}
            name="Available Balance"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PortfolioChart;

