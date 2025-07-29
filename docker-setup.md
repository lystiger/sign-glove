# Sign Glove Docker Setup Guide

## 🐳 Complete Docker Stack

This project now includes a complete Docker setup with:
- **MongoDB** (Database)
- **FastAPI Backend** (Python)
- **React Frontend** (Node.js + Nginx)
- **Optional Redis** (Caching)

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Ensure Docker and Docker Compose are installed
docker --version
docker-compose --version
```

### 2. Environment Setup
```bash
# Copy environment template
cp env.example .env

# Edit .env with your specific values
# ESP32_IP should be your ESP32's actual IP address
```

### 3. Build and Run
```bash
# Build all containers
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### 4. Access Applications
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **MongoDB**: localhost:27017
- **API Docs**: http://localhost:8080/docs

## 📁 Project Structure

```
sign-glove/
├── docker-compose.yml          # Main orchestration
├── .env                        # Environment variables
├── mongo-init/                 # Database initialization
│   └── init.js
├── backend/
│   ├── Dockerfile             # Backend container
│   ├── requirements.txt       # Python dependencies
│   └── .dockerignore
├── frontend/
│   ├── Dockerfile             # Frontend container
│   ├── nginx.conf            # Nginx configuration
│   └── .dockerignore
└── volumes/                   # Persistent data
    ├── mongodb_data/
    ├── backend_data/
    ├── backend_models/
    └── backend_cache/
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# MongoDB
MONGO_URI=mongodb://admin:signglove123@mongodb:27017/signglove?authSource=admin
DB_NAME=signglove

# ESP32
ESP32_IP=192.168.1.100

# TTS
TTS_ENABLED=true
TTS_PROVIDER=gtts

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### Ports
- **3000**: Frontend (React)
- **8080**: Backend (FastAPI)
- **27017**: MongoDB

## 🛠️ Development Commands

### Start Services
```bash
# Start all services
docker-compose up -d

# Start with logs
docker-compose up

# Start specific service
docker-compose up -d backend
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mongodb

# Follow logs
docker-compose logs -f backend
```

### Rebuild
```bash
# Rebuild all
docker-compose build --no-cache

# Rebuild specific service
docker-compose build backend
```

### Database Operations
```bash
# Access MongoDB shell
docker-compose exec mongodb mongosh -u admin -p signglove123

# Backup database
docker-compose exec mongodb mongodump --out /backup

# Restore database
docker-compose exec mongodb mongorestore /backup
```

## 🔍 Health Checks

All services include health checks:
- **Backend**: http://localhost:8080/health
- **Frontend**: http://localhost:3000
- **MongoDB**: Internal ping

Check health status:
```bash
docker-compose ps
```

## 🧹 Maintenance

### Clean Up
```bash
# Remove unused containers, networks, images
docker system prune

# Remove everything including volumes
docker system prune -a --volumes
```

### Update Dependencies
```bash
# Update backend dependencies
docker-compose exec backend pip install -r requirements.txt

# Update frontend dependencies
docker-compose exec frontend npm install
```

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   netstat -ano | findstr :8080
   
   # Kill the process or change port in docker-compose.yml
   ```

2. **MongoDB Connection Issues**
   ```bash
   # Check MongoDB logs
   docker-compose logs mongodb
   
   # Restart MongoDB
   docker-compose restart mongodb
   ```

3. **Build Failures**
   ```bash
   # Clean build
   docker-compose build --no-cache
   
   # Check Dockerfile syntax
   docker build -t test ./backend
   ```

4. **Permission Issues**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

### Debug Mode
```bash
# Run with debug output
docker-compose up --verbose

# Access container shell
docker-compose exec backend bash
docker-compose exec frontend sh
```

## 📊 Monitoring

### Resource Usage
```bash
# Check container resource usage
docker stats

# Check disk usage
docker system df
```

### Log Analysis
```bash
# Search logs
docker-compose logs | grep ERROR

# Export logs
docker-compose logs > logs.txt
```

## 🔒 Security Notes

- Change default MongoDB credentials in production
- Use secrets management for sensitive data
- Enable HTTPS in production
- Regular security updates for base images

## 🚀 Production Deployment

For production, consider:
- Using Docker Swarm or Kubernetes
- Setting up proper logging (ELK stack)
- Implementing monitoring (Prometheus/Grafana)
- Using managed MongoDB service
- Setting up CI/CD pipelines

---

**Happy Dockerizing! 🐳** 