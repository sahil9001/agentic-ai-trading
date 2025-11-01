# Deployment Guide for DigitalOcean

This guide walks you through deploying the Trader AI application to a DigitalOcean droplet with automatic deployment on every GitHub push.

## Prerequisites

- A DigitalOcean account
- A GitHub account
- SSH access to your DigitalOcean server

## Part 1: Initial Server Setup

### Step 1: Create a DigitalOcean Droplet

1. Log in to your DigitalOcean dashboard
2. Click "Create" → "Droplet"
3. Choose:
   - **Image**: Ubuntu 22.04 LTS (or latest)
   - **Plan**: Basic $6/mo (1GB RAM) or higher (recommend 2GB+ for production)
   - **Region**: Choose closest to you
   - **Authentication**: SSH keys (recommended) or password
4. Click "Create Droplet"
5. Wait for droplet creation and note the IP address

### Step 2: Initial Server Configuration

SSH into your droplet:

```bash
ssh root@YOUR_DROPLET_IP
```

Update the system:

```bash
apt update && apt upgrade -y
```

Install Python 3.10+, Node.js, and nginx:

```bash
# Install Python 3.10+ and pip
apt install -y python3 python3-pip python3-venv

# Install Node.js (LTS version)
curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
apt install -y nodejs

# Install nginx
apt install -y nginx

# Install uv (recommended for Python package management)
pip install uv

# Install serve for hosting frontend
npm install -g serve
```

### Step 3: Configure Firewall

```bash
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw allow 8000  # API port
ufw allow 3000  # Frontend port
ufw enable
```

## Part 2: GitHub Actions Setup

### Step 1: Add SSH Key to GitHub Secrets

1. **Generate an SSH key** (if you don't have one):
   ```bash
   ssh-keygen -t rsa -b 4096 -C "github-actions" -f ~/.ssh/github_actions
   ```

2. **Add the public key to your DigitalOcean server**:
   ```bash
   ssh-copy-id -i ~/.ssh/github_actions.pub root@YOUR_DROPLET_IP
   ```

3. **Get the private key**:
   ```bash
   cat ~/.ssh/github_actions
   ```

4. **Add GitHub Secrets**:
   - Go to your GitHub repository
   - Click "Settings" → "Secrets and variables" → "Actions"
   - Click "New repository secret"
   - Add these secrets:
     - `DO_HOST`: Your droplet IP address
     - `DO_USER`: `root` (or your SSH user)
     - `DO_SSH_KEY`: The content of `~/.ssh/github_actions` (private key)

### Step 2: Make deploy.sh Executable

```bash
chmod +x deploy.sh
git add deploy.sh
git commit -m "Add deployment script"
git push
```

### Step 3: Test GitHub Action

The first deployment will happen automatically when you push to the `main` branch:

```bash
git push origin main
```

Monitor the deployment:
1. Go to your GitHub repository
2. Click "Actions" tab
3. Watch the workflow run

## Part 3: Server Configuration

### Step 1: Configure Environment Variables

After the first deployment, SSH into your server and configure `.env`:

```bash
ssh root@YOUR_DROPLET_IP
cd ~/trader-ai
nano .env
```

Add your actual API keys:

```bash
OPENAI_API_KEY=sk-your_actual_openai_key
BINANCE_API_KEY=your_actual_binance_key
BINANCE_SECRET_KEY=your_actual_binance_secret
BINANCE_TESTNET=true
```

### Step 2: Run First Deployment Manually

The deployment script will create all necessary services. Run it once:

```bash
cd ~/trader-ai
bash deploy.sh
```

This will:
- Install Python and Node dependencies
- Build the React frontend
- Create systemd services for all three components
- Configure nginx as a reverse proxy
- Start all services

## Part 4: Service Management

### Check Service Status

```bash
# Check all services
sudo systemctl status trader-ai-main
sudo systemctl status trader-ai-api
sudo systemctl status trader-ai-frontend
sudo systemctl status nginx
```

### View Logs

```bash
# Main trading agent logs
sudo journalctl -u trader-ai-main -f

# API server logs
sudo journalctl -u trader-ai-api -f

# Frontend logs
sudo journalctl -u trader-ai-frontend -f
```

### Manual Service Control

```bash
# Restart a specific service
sudo systemctl restart trader-ai-main
sudo systemctl restart trader-ai-api
sudo systemctl restart trader-ai-frontend

# Stop services
sudo systemctl stop trader-ai-main
sudo systemctl stop trader-ai-api
sudo systemctl stop trader-ai-frontend

# Start services
sudo systemctl start trader-ai-main
sudo systemctl start trader-ai-api
sudo systemctl start trader-ai-frontend
```

## Part 5: Accessing Your Application

Once deployed, access your application:

- **Frontend**: `http://YOUR_DROPLET_IP`
- **API**: `http://YOUR_DROPLET_IP/api/portfolio/history`

### Optional: Setup Custom Domain

1. Point your domain's A record to your droplet IP
2. Update nginx config:

```bash
sudo nano /etc/nginx/sites-available/trader-ai
```

Change `server_name _;` to `server_name yourdomain.com;`

3. Restart nginx:

```bash
sudo systemctl restart nginx
```

## Part 6: Monitoring and Maintenance

### Enable Auto-Updates (Recommended)

```bash
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

### Monitor Disk Space

```bash
df -h
du -sh ~/trader-ai
```

### Backup Database

```bash
# Create a backup script
cat > ~/backup-db.sh << 'EOF'
#!/bin/bash
cp ~/trader-ai/portfolio.db ~/backups/portfolio_$(date +%Y%m%d_%H%M%S).db
find ~/backups -name "portfolio_*.db" -mtime +7 -delete
EOF

chmod +x ~/backup-db.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * ~/backup-db.sh") | crontab -
```

### Set Up Log Rotation

```bash
sudo nano /etc/logrotate.d/trader-ai
```

Add:

```
/var/log/trader-ai/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

## Troubleshooting

### Services Won't Start

1. Check logs: `journalctl -u trader-ai-main -n 50`
2. Verify `.env` file exists and has correct values
3. Check disk space: `df -h`
4. Verify dependencies: `python3 --version`, `node --version`

### Frontend Shows Error

1. Check frontend service: `systemctl status trader-ai-frontend`
2. Check API is running: `curl http://localhost:8000/api/portfolio/history`
3. Check nginx: `systemctl status nginx`
4. View nginx logs: `tail -f /var/log/nginx/error.log`

### API Returns 500 Errors

1. Check database exists: `ls -lh ~/trader-ai/portfolio.db`
2. Check API logs: `journalctl -u trader-ai-api -n 50`
3. Verify Python dependencies: `pip list` or `uv pip list`

### Deployment Fails from GitHub Actions

1. Check Actions logs in GitHub
2. SSH to server and run `deploy.sh` manually
3. Check SSH key is correct in GitHub secrets
4. Verify server has enough resources

## Deployment Architecture

The deployment creates four systemd services:

1. **trader-ai-main**: Runs `main.py` every 5 minutes
2. **trader-ai-api**: Runs `api_server.py` on port 8000
3. **trader-ai-frontend**: Serves React build with `serve` on port 3000
4. **nginx**: Reverse proxy on port 80

All services auto-restart on failure and start on boot.

## Security Considerations

1. **Change SSH port**: Edit `/etc/ssh/sshd_config`
2. **Use firewall**: Already configured with ufw
3. **Keep secrets secret**: Never commit `.env` file
4. **Update regularly**: `apt update && apt upgrade`
5. **Use HTTPS**: Install certbot for Let's Encrypt SSL

### Setup HTTPS (Recommended for Production)

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d yourdomain.com
```

Automatically renews certificates.

## Continuous Deployment Flow

```
Git Push → GitHub Actions → Deploy Script → Systemd Services
    ↓
Services Restart → New Code Running
```

Every push to `main` branch automatically:
1. Checks out code
2. Builds frontend
3. Copies to server
4. Restarts all services

## Next Steps

- Set up monitoring (e.g., Datadog, New Relic)
- Configure alerts (e.g., PagerDuty, email)
- Set up production database backup strategy
- Consider containerization (Docker + Docker Compose)
- Add performance monitoring and analytics

## Support

For issues or questions:
- Check logs: `journalctl -u SERVICE_NAME -f`
- Review GitHub Actions logs
- Open an issue on GitHub

