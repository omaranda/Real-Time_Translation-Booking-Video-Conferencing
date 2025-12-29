# Local Development & Portfolio Setup

This guide is for running the Translation Platform **locally on your machine** for development, testing, or portfolio demonstration purposes.

## ✅ Prerequisites

- **Docker Desktop** installed and running
- **8GB RAM minimum** (Docker needs resources for all services)
- **Ports available**: 3000, 8000, 8443, 5432, 10000

## 🚀 Quick Start (One Command)

```bash
./stack.sh start
```

That's it! Wait 30-60 seconds for all services to start.

## 📍 Access Points

Once started, open these URLs in your browser:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Jitsi Meet (Video Calls)**: http://localhost:8443

## 👤 Test Accounts

Login with these credentials:

| Email | Password | Role |
|-------|----------|------|
| translator1@example.com | password123 | Translator |
| employee@example.com | password123 | Employee |
| admin@example.com | password123 | Admin |

Or register a new translator at: http://localhost:3000/register/translator

## 🎥 Testing Video Calls

### Single Machine Test (Same Browser)

1. Open http://localhost:3000
2. Login as `employee@example.com`
3. Go to Calendar and create a booking
4. Click "Join Call" when ready
5. **Open an incognito/private window**
6. Login as `translator1@example.com`
7. Join the same call
8. Both should see/hear each other

### Multi-Device Test (Same Network)

For testing on **multiple devices on the same WiFi**:

1. **Find your local IP**:
   ```bash
   # macOS/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1

   # Windows
   ipconfig
   ```

2. **Update configuration for network access**:

   Edit `docker-compose.yml`:
   ```yaml
   # Frontend service
   environment:
     NEXT_PUBLIC_API_URL: http://YOUR_IP:8000  # e.g., http://192.168.1.100:8000
     NEXT_PUBLIC_JITSI_DOMAIN: YOUR_IP:8443    # e.g., 192.168.1.100:8443
   ```

   Edit `jitsi-meet/.env`:
   ```bash
   DOCKER_HOST_ADDRESS=YOUR_IP        # e.g., 192.168.1.100
   PUBLIC_URL=http://YOUR_IP:8443     # e.g., http://192.168.1.100:8443
   JVB_WS_DOMAIN=YOUR_IP:8443         # e.g., 192.168.1.100:8443
   ```

   Edit `docker-compose.yml` (JVB section):
   ```yaml
   jitsi-jvb:
     environment:
       - JVB_WS_DOMAIN=YOUR_IP:8443   # e.g., 192.168.1.100:8443
   ```

3. **Restart stack**:
   ```bash
   ./stack.sh restart
   ```

4. **Access from other devices**:
   - Phone/Tablet: http://YOUR_IP:3000
   - Another laptop: http://YOUR_IP:3000

## ⚙️ Configuration Files

The platform is configured for **localhost-only** by default:

### docker-compose.yml
```yaml
frontend:
  environment:
    NEXT_PUBLIC_API_URL: http://localhost:8000
    NEXT_PUBLIC_JITSI_DOMAIN: localhost:8443

jitsi-jvb:
  environment:
    - JVB_WS_DOMAIN=localhost:8443
    - JVB_DISABLE_STUN=true  # Disables external STUN for local testing
```

### jitsi-meet/.env
```bash
DOCKER_HOST_ADDRESS=localhost
PUBLIC_URL=http://localhost:8443
JVB_WS_DOMAIN=localhost:8443
ENABLE_AUTH=0                # No authentication required for testing
ENABLE_GUESTS=1              # Anyone can join
```

## 🐛 Troubleshooting

### Calls Keep Restarting/Disconnecting

**Problem**: Video calls disconnect and restart repeatedly.

**Solution**: This is usually a WebRTC ICE configuration issue.

1. **Check Jitsi logs**:
   ```bash
   ./stack.sh logs jitsi-jvb
   ```

2. **Verify configuration** in `jitsi-meet/.env`:
   ```bash
   DOCKER_HOST_ADDRESS=localhost  # Should match how you access the app
   JVB_WS_DOMAIN=localhost:8443   # Should match Jitsi URL
   ```

3. **Disable STUN** for local testing in `docker-compose.yml`:
   ```yaml
   jitsi-jvb:
     environment:
       - JVB_DISABLE_STUN=true
   ```

4. **Restart Jitsi services**:
   ```bash
   docker restart callcenter-jitsi-jvb callcenter-jitsi-web
   ```

### Frontend Shows "Unhealthy" Status

**Problem**: `./stack.sh status` shows frontend as unhealthy.

**Solution**: This is often a timing issue during startup.

```bash
# Wait a bit longer (Next.js can take 30-60 seconds)
sleep 30 && ./stack.sh status

# Check frontend logs
./stack.sh logs frontend

# If still failing, rebuild
./stack.sh restart
```

### Port Already in Use

**Problem**: "Port 3000/8000/8443 already in use"

**Solution**:
```bash
# Find what's using the port
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Kill the process or change the port in docker-compose.yml
# Example: Change frontend port to 3001
ports:
  - "3001:3000"
```

### Database Connection Failed

**Problem**: Backend can't connect to database.

**Solution**:
```bash
# Check database is running
docker ps | grep postgres

# Check database logs
./stack.sh logs database

# Restart database
docker restart callcenter-postgres

# Verify database is healthy
./stack.sh status
```

### Video/Audio Not Working

**Problem**: Camera or microphone permissions denied.

**Solution**:
1. Modern browsers **require HTTPS for media devices** OR **localhost**
2. For localhost, always access via `http://localhost:8443`, NOT `http://127.0.0.1:8443`
3. When prompted, **allow camera/microphone permissions**
4. Check browser console for errors (F12 → Console tab)

### Can't Access from Another Device

**Problem**: Phone/tablet can't access `http://localhost:3000`

**Solution**: Use your machine's IP address instead (see "Multi-Device Test" above).

## 🛑 Stopping the Stack

```bash
# Stop all services (keeps data)
./stack.sh stop

# Stop and remove everything including database data
./stack.sh clean
```

## 📊 Monitoring

### View Logs
```bash
# All services
./stack.sh logs

# Specific service
./stack.sh logs backend
./stack.sh logs frontend
./stack.sh logs jitsi-jvb
./stack.sh logs database
```

### Check Health
```bash
./stack.sh status
```

### Database Access
```bash
# PostgreSQL CLI
docker exec -it callcenter-postgres psql -U callcenter -d callcenter

# View users
docker exec -it callcenter-postgres psql -U callcenter -c "SELECT email, name, role FROM users;"
```

## 🎯 Portfolio Demo Tips

### For Showcasing to Recruiters/Clients:

1. **Prepare test data**: Use the seed data (translators, bookings)
2. **Test beforehand**: Ensure video calls work on your setup
3. **Have backup**: Record a video demo in case live demo fails
4. **Use two browsers**: Chrome for client, Firefox for translator (easier to demo)
5. **Explain the architecture**: Show the Docker Compose setup, microservices approach

### Key Features to Highlight:

- ✅ **Full-stack**: Next.js frontend + FastAPI backend
- ✅ **Real-time video**: Self-hosted Jitsi Meet integration
- ✅ **Containerized**: Docker Compose orchestration
- ✅ **Database**: PostgreSQL with proper schema design
- ✅ **Auth**: JWT-based authentication
- ✅ **Cloud-ready**: Terraform infrastructure as code for AWS

## 🔄 Updating the Application

### Pull Latest Changes
```bash
git pull origin main
./stack.sh build    # Rebuild images
./stack.sh restart  # Restart with new code
```

### Database Migrations
```bash
# If you add new database changes, update init.sql and:
./stack.sh clean    # Warning: deletes all data!
./stack.sh start    # Recreates database with new schema
```

## 📝 Important Notes

### Localhost vs IP Address

The app is configured for **localhost** by default. This means:

- ✅ **Works**: Access from the same machine via http://localhost:3000
- ❌ **Won't work**: Access from phone/tablet via http://localhost:3000
- ✅ **Works for network**: Change config to use your IP (192.168.x.x)

### Browser Compatibility

Jitsi works best with:
- ✅ Chrome/Chromium (recommended)
- ✅ Firefox
- ✅ Edge
- ⚠️ Safari (some features limited)
- ❌ IE11 (not supported)

### Performance

If your machine is slow:
- Reduce Docker resource limits
- Run backend/frontend locally (not in Docker)
- Use fewer concurrent services

## 🆘 Getting Help

1. **Check logs first**: `./stack.sh logs`
2. **Review troubleshooting section** above
3. **Check GitHub Issues**: Look for similar problems
4. **Stack overflow tags**: `docker`, `jitsi`, `fastapi`, `nextjs`

## 📚 Next Steps

- Read [README.md](../README.md) for complete platform overview
- See [JITSI_SETUP.md](JITSI_SETUP.md) for advanced Jitsi configuration
- Check [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md) for production deployment
- Review [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing

---

**Ready to demo your portfolio!** 🎉
