import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';

const BASE_VALUE = 5000;

const PortfolioChart = ({ data }) => {
  // Format data for the chart with profit/loss calculation
  const chartData = data.map(item => {
    const total = parseFloat(item.total);
    const change = total - BASE_VALUE;
    const percentChange = ((change / BASE_VALUE) * 100).toFixed(2);
    
    return {
      time: new Date(item.timestamp).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }),
      timestamp: item.timestamp,
      total: total,
      change: change,
      percentChange: percentChange,
      isProfit: change >= 0
    };
  });

  // Calculate Y-axis domain to center around 5000
  const values = chartData.map(d => d.total);
  const minValue = Math.min(...values, BASE_VALUE);
  const maxValue = Math.max(...values, BASE_VALUE);
  const range = Math.max(maxValue - BASE_VALUE, BASE_VALUE - minValue);
  const yAxisDomain = [
    BASE_VALUE - range * 1.1,
    BASE_VALUE + range * 1.1
  ];

  // Get line color based on latest value
  const latestData = chartData[chartData.length - 1];
  const lineColor = latestData?.isProfit ? '#10b981' : '#ef4444';

  // Format timestamp to IST (Indian Standard Time, UTC+5:30)
  const formatIST = (timestamp) => {
    const date = new Date(timestamp);
    
    return date.toLocaleString('en-IN', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
      timeZone: 'Asia/Kolkata'
    }) + ' IST';
  };

  // Custom tooltip formatter
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const change = data.change;
      const isProfit = change >= 0;
      const istTime = formatIST(data.timestamp);
      
      return (
        <div className="custom-tooltip" style={{
          backgroundColor: 'white',
          padding: '12px 16px',
          border: '1px solid #e5e7eb',
          borderRadius: '6px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
          fontSize: '0.875rem'
        }}>
          <p style={{ 
            margin: '0 0 8px 0', 
            fontWeight: 500,
            color: '#1a1a1a',
            fontSize: '0.75rem',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            {istTime}
          </p>
          <p style={{ 
            margin: '0 0 4px 0', 
            fontWeight: 600,
            color: '#1a1a1a',
            fontSize: '1.125rem'
          }}>
            ${data.total.toFixed(2)}
          </p>
          <p style={{ 
            margin: 0, 
            color: isProfit ? '#10b981' : '#ef4444',
            fontWeight: 500,
            fontSize: '0.875rem'
          }}>
            {isProfit ? '+' : ''}{data.change.toFixed(2)} ({isProfit ? '+' : ''}{data.percentChange}%)
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{ top: 20, right: 20, left: 20, bottom: 40 }}
        >
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="#f0f0f0" 
            vertical={false}
          />
          <ReferenceLine 
            y={BASE_VALUE} 
            stroke="#d1d5db" 
            strokeWidth={1}
            strokeDasharray="2 2"
            label={{ value: 'Base ($5,000)', position: 'right', fill: '#9ca3af', fontSize: 12 }}
          />
          <XAxis
            dataKey="time"
            hide={true}
          />
          <YAxis
            stroke="#9ca3af"
            tick={{ fill: '#6b7280', fontSize: 12 }}
            tickFormatter={(value) => {
              const diff = value - BASE_VALUE;
              if (diff === 0) return '$5,000';
              const sign = diff > 0 ? '+' : '';
              return `${sign}$${diff.toFixed(0)}`;
            }}
            domain={yAxisDomain}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="linear"
            dataKey="total"
            stroke={lineColor}
            strokeWidth={2.5}
            dot={false}
            activeDot={{ r: 6, fill: lineColor, strokeWidth: 2, stroke: 'white' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PortfolioChart;

