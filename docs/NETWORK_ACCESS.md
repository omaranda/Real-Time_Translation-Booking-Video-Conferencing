# Network Access Guide - No Hosts File Required!

This guide explains how to access the Interpretation Platform from any device on your network using **IP addresses only** - no hosts file modifications needed!

## Your Network Configuration

**Host Machine IP:** `192.168.2.134`

## Access URLs

### From Your Main Computer (Host Machine)

You can use either the domain or IP:

| Service | Domain URL | IP URL |
|---------|-----------|---------|
| Frontend | http://app.interpretation-service.com:3000 | http://192.168.2.134:3000 |
| Backend API | http://app.interpretation-service.com:8000 | http://192.168.2.134:8000 |
| Jitsi Meet | http://meet.interpretation-service.com:8443 | http://192.168.2.134:8443 |

### From Other Devices (Phones, Tablets, Other Computers)

**Simply use the IP addresses - no configuration needed!**

| Service | Access URL |
|---------|-----------|
| **Main Application** | **http://192.168.2.134:3000** |
| Backend API | http://192.168.2.134:8000 |
| Jitsi Meet | http://192.168.2.134:8443 |

## Quick Start

### 1. On Your Host Machine

The domain-based setup is already configured and working:

```bash
# Services are already running
docker-compose ps

# Access the app
open http://app.interpretation-service.com:3000
```

### 2. On Other Devices (Network Access)

**No setup required!** Just open your browser and go to:

```
http://192.168.2.134:3000
```

**That's it!** No hosts file, no DNS configuration, nothing to install.

## Login Credentials

| Email | Password | Role |
|-------|----------|------|
| admin@example.com | password123 | Admin |
| agent1@example.com | password123 | Agent |
| supervisor@example.com | password123 | Supervisor |

## Testing Video Calls Across Devices

### Scenario: Test call between your computer and phone

**On your computer:**
1. Go to: http://192.168.2.134:3000 (or http://app.interpretation-service.com:3000 if you have hosts file)
2. Login and create/join a call
3. Note the room name

**On your phone:**
1. Open browser and go to: http://192.168.2.134:3000
2. Login with a different account
3. Join the same room
4. Video call should work!

**Important:** Video calls **always use** `http://192.168.2.134:8443` regardless of how you access the app (IP or domain). This means:
- ✅ No hosts file needed for Jitsi to work
- ✅ Works even if you access via domain but don't have meet.interpretation-service.com in hosts

## Network Requirements

### Firewall

Ensure these ports are accessible on your host machine (`192.168.2.134`):

| Port | Protocol | Service |
|------|----------|---------|
| 3000 | TCP | Frontend |
| 8000 | TCP | Backend API |
| 8443 | TCP | Jitsi Web Interface |
| 10000 | UDP | Jitsi Video/Audio (RTP) |

### macOS Firewall Configuration

```bash
# Check if firewall is blocking
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# If enabled, allow Docker
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /Applications/Docker.app
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblock /Applications/Docker.app
```

## Troubleshooting

### "Cannot connect from other device"

**1. Verify host machine IP:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

**2. Test from another device:**
```bash
# From another computer/phone, ping the host
ping 192.168.2.134
```

**3. Check Docker ports are bound:**
```bash
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

Should show ports like `0.0.0.0:3000->3000/tcp`

**4. Test direct connection:**
```bash
# From another device
curl http://192.168.2.134:8000/health
```

### "Video calls not working"

**1. Check UDP port 10000 is not blocked:**
```bash
# On host machine
sudo lsof -i UDP:10000
```

**2. Verify JVB is running:**
```bash
docker logs callcenter-jitsi-jvb | tail -20
```

**3. Check WebSocket connection in browser console** (F12):
- Should connect to: `ws://192.168.2.134:8443/xmpp-websocket`
- Look for WebSocket errors

### "CORS errors in browser"

The backend is already configured to allow:
- ✅ `http://192.168.2.134:3000`
- ✅ `http://192.168.2.134:8443`

If you see CORS errors, check the origin in browser console and add it to [backend/app/main.py](backend/app/main.py).

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Local Network (192.168.2.x)                        │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │  Host Machine: 192.168.2.134                   │ │
│  │                                                 │ │
│  │  Docker Services:                              │ │
│  │  ├─ Frontend    :3000 → 0.0.0.0:3000          │ │
│  │  ├─ Backend     :8000 → 0.0.0.0:8000          │ │
│  │  ├─ Jitsi Web   :8443 → 0.0.0.0:8443          │ │
│  │  ├─ Jitsi JVB   :10000/udp → 0.0.0.0:10000    │ │
│  │  └─ PostgreSQL  :5432                          │ │
│  └────────────────────────────────────────────────┘ │
│                         ▲                            │
│                         │ HTTP Requests              │
│                         │                            │
│  ┌─────────────────────┴────────────────────────┐  │
│  │  Other Devices Access Via IP:               │  │
│  │  http://192.168.2.134:3000                   │  │
│  │                                               │  │
│  │  ✓ Laptops     ✓ Phones                      │  │
│  │  ✓ Tablets     ✓ Desktop PCs                 │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Advantages of IP-Based Access

✅ **No configuration required** on client devices
✅ **Works immediately** - just open a browser
✅ **No DNS or hosts file** modifications needed
✅ **Easy to share** - just send the IP address
✅ **Works on mobile** devices without special setup
✅ **Production-ready** - can switch to real domain later

## Switching to Production

When deploying to production with a real domain:

1. **Get a real domain:** `yourdomain.com`
2. **Set up DNS A records:**
   - `app.yourdomain.com` → Your server IP
   - `meet.yourdomain.com` → Your server IP
3. **Enable HTTPS** with Let's Encrypt certificates
4. **Update environment variables** in docker-compose
5. **Update CORS** to allow production domains

The IP-based access will continue to work alongside the domain!

## Security Notes

**For Local Network Use:**
- ✅ HTTP is acceptable (traffic stays on local network)
- ✅ No external exposure
- ✅ Firewall protects from internet access

**For Production/Internet:**
- ⚠️ Must use HTTPS
- ⚠️ Configure proper authentication
- ⚠️ Use secure Jitsi settings (JWT auth)
- ⚠️ Set up proper firewall rules

## Summary

**Frontend access:**
- Your main computer: `http://app.interpretation-service.com:3000` (with hosts file) or `http://192.168.2.134:3000` ✓
- All other devices: `http://192.168.2.134:3000` ✓

**Jitsi video calls:**
- **Always use:** `http://192.168.2.134:8443` (hardcoded for all access methods)
- No domain resolution needed - works without hosts file ✓

**Key Benefits:**
- ✅ No hosts file required for Jitsi
- ✅ Video calls work from any device
- ✅ Simple IP-based access for everything
