#!/bin/bash
set -e

echo "=== Starting Deployment ==="

# Navigate to project directory
source ~/.bashrc
cd ~/trader-ai

# Step 1: Update Python dependencies
echo "Step 1: Installing/updating Python dependencies..."
if command -v uv &> /dev/null; then
    uv sync
else
    echo "uv not found, using pip..."
    pip install -e .
fi

# Step 2: Create .env file if it doesn't exist
echo "Step 2: Checking environment variables..."
if [ ! -f .env ]; then
    echo "WARNING: .env file not found. Creating from template..."
    cat > .env << 'EOF'
OPENAI_API_KEY=your_openai_api_key_here
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET_KEY=your_binance_secret_key_here
BINANCE_TESTNET=true
EOF
    echo "Please edit ~/trader-ai/.env with your actual API keys"
fi

# Step 3: Stop existing services
echo "Step 3: Stopping existing services..."
sudo systemctl stop trader-ai-main || true
sudo systemctl stop trader-ai-api || true
sudo systemctl stop trader-ai-frontend || true

# Step 4: Setup Frontend
echo "Step 4: Setting up frontend..."
cd frontend
npm install --production
npm run build
cd ..

# Step 5: Create systemd service files
echo "Step 5: Creating systemd service files..."

# Main trading agent service
sudo tee /etc/systemd/system/trader-ai-main.service > /dev/null << 'EOF'
[Unit]
Description=Trader AI Main Trading Agent
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/trader-ai
Environment="PATH=/root/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# API server service
sudo tee /etc/systemd/system/trader-ai-api.service > /dev/null << 'EOF'
[Unit]
Description=Trader AI API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/trader-ai
Environment="PATH=/root/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 api_server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Frontend service (using serve)
sudo tee /etc/systemd/system/trader-ai-frontend.service > /dev/null << 'EOF'
[Unit]
Description=Trader AI Frontend
After=network.target trader-ai-api.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/trader-ai/frontend/build
Environment="PORT=3000"
Environment="REACT_APP_API_URL=http://localhost:8000"
ExecStart=/usr/bin/npx serve -s . -l 3000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Step 6: Install nginx and serve if needed
echo "Step 6: Installing additional dependencies..."
sudo apt-get update
sudo apt-get install -y nginx || true
npm install -g serve || true

# Step 7: Configure nginx
echo "Step 7: Configuring nginx..."
sudo tee /etc/nginx/sites-available/trader-ai > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/trader-ai /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# Step 8: Reload systemd and start services
echo "Step 8: Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable trader-ai-main
sudo systemctl enable trader-ai-api
sudo systemctl enable trader-ai-frontend

sudo systemctl start trader-ai-main
sudo systemctl start trader-ai-api
sudo systemctl start trader-ai-frontend

# Step 9: Check service status
echo "Step 9: Checking service status..."
sleep 5
sudo systemctl status trader-ai-main --no-pager -l
sudo systemctl status trader-ai-api --no-pager -l
sudo systemctl status trader-ai-frontend --no-pager -l

echo "=== Deployment Complete ==="
echo "Services should now be running:"
echo "  - Main agent: systemctl status trader-ai-main"
echo "  - API: systemctl status trader-ai-api"
echo "  - Frontend: systemctl status trader-ai-frontend"
echo "  - Nginx: systemctl status nginx"
echo ""
echo "Logs can be viewed with:"
echo "  - sudo journalctl -u trader-ai-main -f"
echo "  - sudo journalctl -u trader-ai-api -f"
echo "  - sudo journalctl -u trader-ai-frontend -f"

