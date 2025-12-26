# Local Network Setup Guide

This guide will help you set up the Interpretation Platform with a local domain for testing across your network.

## Overview

The platform uses the local domain `interpretation-service.com` with the following subdomains:
- `app.interpretation-service.com:3000` - Main application frontend
- `meet.interpretation-service.com:8443` - Jitsi Meet video conferencing
- `app.interpretation-service.com:8000` - Backend API

## Step 1: Configure DNS (Hosts File)

You need to add these domains to the `/etc/hosts` file on **every device** that will access the platform.

### On Your Host Machine (Mac)

1. Open Terminal and edit the hosts file:
   ```bash
   sudo nano /etc/hosts
   ```

2. Add these lines (replace `192.168.2.134` with your actual local IP):
   ```
   192.168.2.134   app.interpretation-service.com
   192.168.2.134   meet.interpretation-service.com
   ```

3. Save and exit (Ctrl+O, Enter, Ctrl+X)

4. Flush DNS cache:
   ```bash
   sudo dscacheutil -flushcache
   sudo killall -HUP mDNSResponder
   ```

### On Other Computers in Your Network

#### macOS
Same as above, but use the IP address of the machine running Docker (192.168.2.134)

#### Windows
1. Open Notepad as Administrator
2. Open file: `C:\Windows\System32\drivers\etc\hosts`
3. Add these lines:
   ```
   192.168.2.134   app.interpretation-service.com
   192.168.2.134   meet.interpretation-service.com
   ```
4. Save the file
5. Flush DNS: `ipconfig /flushdns` in Command Prompt

#### Linux
1. Edit hosts file:
   ```bash
   sudo nano /etc/hosts
   ```
2. Add the same lines as macOS
3. Save and exit

#### Mobile Devices (iOS/Android)

For mobile testing, you have two options:

**Option 1: Use IP addresses directly**
- Access via `http://192.168.2.134:3000` (may have CORS issues)

**Option 2: Set up a local DNS server** (Recommended)
- Install Pi-hole or dnsmasq on your network
- Configure it to resolve `*.interpretation-service.com` to `192.168.2.134`

## Step 2: Start the Services

```bash
# Stop existing services
docker-compose down

# Rebuild and start all services
docker-compose up -d --build

# Check status
docker-compose ps
```

## Step 3: Verify the Setup

1. **Test DNS Resolution:**
   ```bash
   ping app.interpretation-service.com
   ping meet.interpretation-service.com
   ```
   Both should resolve to `192.168.2.134`

2. **Test Frontend:**
   Open browser: `http://app.interpretation-service.com:3000`

3. **Test Backend API:**
   ```bash
   curl http://app.interpretation-service.com:8000/health
   ```

4. **Test Jitsi:**
   Open browser: `http://meet.interpretation-service.com:8443`

## Step 4: Testing Video Calls

1. Open the app on your main computer: `http://app.interpretation-service.com:3000`
2. Log in and start/join a call
3. On another device (phone, tablet, another computer):
   - Add the hosts entries (see Step 1)
   - Open `http://app.interpretation-service.com:3000`
   - Join the same call

## Network Configuration

### Firewall Rules

Ensure these ports are open on your host machine:

| Port  | Protocol | Service | Description |
|-------|----------|---------|-------------|
| 3000  | TCP      | Frontend | Next.js application |
| 8000  | TCP      | Backend | FastAPI backend |
| 8443  | TCP      | Jitsi Web | Jitsi Meet web interface |
| 10000 | UDP      | JVB | Jitsi Video Bridge media |
| 4443  | TCP      | JVB | Jitsi Video Bridge fallback |

### macOS Firewall

```bash
# Allow incoming connections (if firewall is enabled)
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /Applications/Docker.app
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblock /Applications/Docker.app
```

## Troubleshooting

### Issue: Cannot access from other devices

1. **Check firewall:**
   ```bash
   # Temporarily disable macOS firewall to test
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off
   ```

2. **Verify ports are listening:**
   ```bash
   netstat -an | grep -E "3000|8000|8443|10000"
   ```

3. **Check Docker port bindings:**
   ```bash
   docker port callcenter-frontend
   docker port callcenter-jitsi-web
   ```

### Issue: Jitsi calls not connecting

1. **Check JVB logs:**
   ```bash
   docker logs callcenter-jitsi-jvb | grep -i "websocket\|colibri"
   ```

2. **Verify WebSocket configuration:**
   ```bash
   docker exec callcenter-jitsi-jvb cat /config/jvb.conf | grep -A5 websockets
   ```

   Should show:
   ```
   websockets {
       enabled = true
       domain = "meet.interpretation-service.com:8443"
       tls = false
       server-id = "default-jvb"
   }
   ```

### Issue: DNS not resolving

1. **Clear browser cache**
2. **Try incognito/private mode**
3. **Restart browser completely**
4. **Verify hosts file was saved correctly:**
   ```bash
   cat /etc/hosts | grep interpretation-service
   ```

## Network Topology

```
┌─────────────────────────────────────────────┐
│  Your Local Network (192.168.2.0/24)       │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  Host Machine (192.168.2.134)        │  │
│  │                                      │  │
│  │  Docker Containers:                  │  │
│  │  ├─ Frontend    :3000                │  │
│  │  ├─ Backend     :8000                │  │
│  │  ├─ Jitsi Web   :8443                │  │
│  │  ├─ Jitsi JVB   :10000 (UDP)         │  │
│  │  └─ PostgreSQL  :5432                │  │
│  └──────────────────────────────────────┘  │
│                     ▲                       │
│                     │                       │
│  ┌──────────────────┴───────────────────┐  │
│  │  Other Devices                       │  │
│  │  - Laptops                           │  │
│  │  - Phones                            │  │
│  │  - Tablets                           │  │
│  │  Access via:                         │  │
│  │  app.interpretation-service.com:3000 │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

## Production Deployment Notes

When deploying to production:

1. Replace `interpretation-service.com` with your actual domain
2. Enable HTTPS/TLS with proper certificates
3. Use a real DNS service instead of hosts file
4. Configure proper firewall rules
5. Set up TURN/STUN servers for NAT traversal
6. Enable authentication on Jitsi

## Support

For issues or questions, check:
- Docker logs: `docker-compose logs -f [service-name]`
- Browser console for JavaScript errors
- Network tab in browser DevTools for failed requests
