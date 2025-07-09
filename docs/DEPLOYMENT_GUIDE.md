# 🚀 Deployment Guide - Smart Shipment Entry Tool

This guide covers various deployment options for the Smart Shipment Entry Tool, from local development to production deployment.

## 📋 Prerequisites

- Python 3.8+ installed
- Git (for version control)
- Your Excel template file
- Optional: OpenAI API key for enhanced accuracy

## 🏠 Local Development Setup

### Step 1: Environment Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd excel-automation

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file (optional - works without API key)
nano .env
```

Add your OpenAI API key if you have one:
```
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4
```

### Step 3: Run Locally
```bash
streamlit run app.py
```

Access the application at: `http://localhost:8501`

## ☁️ Streamlit Cloud Deployment (Recommended)

Streamlit Cloud is the easiest way to deploy and share your application.

### Step 1: Prepare Repository
1. Push your code to GitHub
2. Ensure your repository includes:
   - `requirements.txt`
   - `app.py`
   - All source files in `src/`
   - Your Excel template file

### Step 2: Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file path: `app.py`
6. Click "Deploy"

### Step 3: Configure Secrets (Optional)
If using OpenAI API:
1. Go to your app settings
2. Click "Secrets"
3. Add:
```toml
OPENAI_API_KEY = "sk-your-api-key-here"
OPENAI_MODEL = "gpt-4"
```

### Benefits of Streamlit Cloud:
- ✅ Free hosting
- ✅ Automatic updates from GitHub
- ✅ HTTPS by default
- ✅ Easy sharing with team
- ✅ Built-in authentication options

## 🐳 Docker Deployment

For containerized deployment on any platform.

### Step 1: Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Step 2: Build and Run
```bash
# Build Docker image
docker build -t shipment-tool .

# Run container
docker run -p 8501:8501 shipment-tool
```

### Step 3: Docker Compose (Optional)
Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  shipment-tool:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./output:/app/output
    restart: unless-stopped
```

Run with: `docker-compose up -d`

## 🌐 Cloud Platform Deployment

### Heroku Deployment

1. **Create Heroku app**:
```bash
heroku create your-app-name
```

2. **Add buildpack**:
```bash
heroku buildpacks:set heroku/python
```

3. **Create Procfile**:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

4. **Deploy**:
```bash
git push heroku main
```

5. **Set environment variables**:
```bash
heroku config:set OPENAI_API_KEY=your-key-here
```

### AWS EC2 Deployment

1. **Launch EC2 instance** (Ubuntu 20.04 LTS)
2. **Install dependencies**:
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
```

3. **Setup application**:
```bash
git clone <your-repo>
cd excel-automation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Create systemd service** (`/etc/systemd/system/shipment-tool.service`):
```ini
[Unit]
Description=Shipment Tool
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/excel-automation
Environment=PATH=/home/ubuntu/excel-automation/venv/bin
ExecStart=/home/ubuntu/excel-automation/venv/bin/streamlit run app.py --server.port=8501
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Start service**:
```bash
sudo systemctl enable shipment-tool
sudo systemctl start shipment-tool
```

6. **Configure Nginx** (optional, for custom domain):
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 🔒 Security Considerations

### API Key Security
- Never commit API keys to version control
- Use environment variables or secrets management
- Rotate keys regularly
- Monitor API usage

### File Security
- Validate uploaded files
- Limit file sizes
- Sanitize file names
- Use temporary directories for processing

### Access Control
- Consider adding authentication for sensitive deployments
- Use HTTPS in production
- Implement rate limiting if needed

## 📊 Monitoring and Maintenance

### Health Monitoring
```python
# Add to app.py for health checks
import streamlit as st

def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Add endpoint: /health
```

### Log Management
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Backup Strategy
- Regular backups of Excel templates
- Archive processed files
- Database backups if using persistent storage

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use**:
```bash
streamlit run app.py --server.port=8502
```

2. **Memory issues with large files**:
- Increase container memory limits
- Implement file size restrictions
- Use streaming for large datasets

3. **API rate limits**:
- Implement exponential backoff
- Use fallback parsing mode
- Monitor API usage

4. **Excel template not found**:
- Check file path in config
- Ensure file is included in deployment
- Verify file permissions

### Performance Optimization
- Use caching for repeated operations
- Optimize Excel processing
- Implement async processing for large batches
- Use CDN for static assets

## 📞 Support

For deployment issues:
1. Check the logs first
2. Verify all dependencies are installed
3. Ensure environment variables are set correctly
4. Test with minimal configuration
5. Check firewall and network settings

## 🔄 Updates and Maintenance

### Updating the Application
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart shipment-tool
```

### Backup Before Updates
```bash
# Backup current version
cp -r excel-automation excel-automation-backup-$(date +%Y%m%d)

# Backup database/files
tar -czf backup-$(date +%Y%m%d).tar.gz output/ templates/
```

This deployment guide should help you get the Smart Shipment Entry Tool running in any environment, from local development to production cloud deployment.
