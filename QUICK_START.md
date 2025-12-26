# Quick Start Guide - Local Network Setup

## What's New

The platform now uses the local domain `interpretation-service.com` for better configuration and local network testing. This allows:

- ✅ Clean, consistent URLs across all services
- ✅ Easy testing on multiple devices in your network
- ✅ Proper WebSocket configuration for Jitsi calls
- ✅ COLIBRI WebSocket enabled for better performance

## Before You Start

Your host machine IP: **192.168.2.134**

## Setup Steps

### 1. Configure Local DNS (Required)

Run the setup script to add domain entries to your hosts file:

```bash
./setup-hosts.sh
```

This will add these entries to `/etc/hosts`:
```
127.0.0.1   app.interpretation-service.com
127.0.0.1   meet.interpretation-service.com
```

### 2. Start the Services

```bash
# Stop any running containers
docker-compose down

# Rebuild and start all services
docker-compose up -d --build

# Watch the logs (optional)
docker-compose logs -f
```

### 3. Access the Application

Once all services are running:

- **Frontend**: http://app.interpretation-service.com:3000
- **Backend API**: http://app.interpretation-service.com:8000
- **API Docs**: http://app.interpretation-service.com:8000/docs
- **Jitsi Meet**: http://meet.interpretation-service.com:8443

### 4. Login Credentials

Use these test accounts to log in:

| Email | Password | Role |
|-------|----------|------|
| admin@example.com | password123 | Admin |
| agent1@example.com | password123 | Agent |
| agent2@example.com | password123 | Agent |
| supervisor@example.com | password123 | Supervisor |

**Translators** can self-register at: http://app.interpretation-service.com:3000/register/translator

## Testing on Other Devices

### On Other Computers (Same Network)

1. **Add hosts entries** on the other computer:

   **macOS/Linux:**
   ```bash
   sudo nano /etc/hosts
   ```
   Add:
   ```
   192.168.2.134   app.interpretation-service.com
   192.168.2.134   meet.interpretation-service.com
   ```

   **Windows:**
   - Edit `C:\Windows\System32\drivers\etc\hosts` as Administrator
   - Add the same lines

2. **Access the app:**
   - Open: http://app.interpretation-service.com:3000

### On Mobile Devices

For mobile testing, you can:

**Option 1**: Use IP directly (may have issues)
- http://192.168.2.134:3000

**Option 2**: Set up local DNS server (recommended)
- Install Pi-hole or similar DNS server
- Configure to resolve `*.interpretation-service.com` → `192.168.2.134`

## Configuration Summary

### Services and Ports

| Service | URL | Port |
|---------|-----|------|
| Frontend | app.interpretation-service.com | 3000 |
| Backend | app.interpretation-service.com | 8000 |
| Jitsi Meet | meet.interpretation-service.com | 8443 |
| PostgreSQL | localhost | 5432 |
| JVB Media | - | 10000/udp |

### Key Configuration Files Changed

1. **[jitsi-meet/.env](jitsi-meet/.env)**
   - `PUBLIC_URL=http://meet.interpretation-service.com:8443`
   - `ENABLE_COLIBRI_WEBSOCKET=1` (re-enabled)
   - `JVB_WS_DOMAIN=meet.interpretation-service.com:8443`

2. **[docker-compose.yml](docker-compose.yml)**
   - `NEXT_PUBLIC_JITSI_DOMAIN: meet.interpretation-service.com:8443`
   - `NEXT_PUBLIC_API_URL: http://app.interpretation-service.com:8000`

3. **[frontend/src/components/JitsiCall.tsx](frontend/src/components/JitsiCall.tsx)**
   - Updated to detect local domains and use HTTP protocol

## Troubleshooting

### "Cannot connect to service"

1. Verify hosts file:
   ```bash
   ping app.interpretation-service.com
   ```
   Should resolve to `127.0.0.1` on host machine or `192.168.2.134` on other devices

2. Check services are running:
   ```bash
   docker-compose ps
   ```
   All should show "Up" status

### "Jitsi call crashes"

1. Check JVB WebSocket configuration:
   ```bash
   docker logs callcenter-jitsi-jvb | grep websocket
   ```
   Should show:
   ```
   Websockets enabled, but no domains specified: URLs=[ws://meet.interpretation-service.com:8443/colibri-ws/default-jvb]
   ```

2. Check browser console for errors
3. Verify port 10000/UDP is not blocked by firewall

### "Cannot access from other devices"

1. Check macOS firewall settings
2. Verify Docker port bindings:
   ```bash
   docker port callcenter-frontend
   docker port callcenter-jitsi-web
   ```
3. Test direct connection:
   ```bash
   curl http://192.168.2.134:3000
   ```

## Reverting to localhost

If you want to revert to localhost-only setup:

1. Edit `docker-compose.yml`:
   - Change `meet.interpretation-service.com:8443` → `localhost:8443`
   - Change `app.interpretation-service.com:8000` → `localhost:8000`

2. Edit `jitsi-meet/.env`:
   - Change `PUBLIC_URL=http://localhost:8443`
   - Change `JVB_WS_DOMAIN=localhost:8443`

3. Rebuild:
   ```bash
   docker-compose up -d --build
   ```

## Next Steps

For detailed information:
- See [LOCAL_NETWORK_SETUP.md](LOCAL_NETWORK_SETUP.md) for comprehensive setup guide
- See [docs/JITSI_SETUP.md](docs/JITSI_SETUP.md) for Jitsi-specific configuration

## What Was Fixed

### Previous Issues

1. ❌ Jitsi calls crashed and returned to lobby
2. ❌ Malformed WebSocket URLs (`wss://http://...`)
3. ❌ COLIBRI WebSocket disabled due to TLS issues
4. ❌ Hard to test on multiple devices
5. ❌ Users couldn't log in (CORS errors)
6. ❌ Call links used localhost instead of domain
7. ❌ App redirected to meet.jit.si instead of local Jitsi

### Solutions Applied

1. ✅ Fixed WebSocket domain configuration
2. ✅ Re-enabled COLIBRI WebSocket with proper HTTP config
3. ✅ Set up local domain for clean configuration
4. ✅ Updated all service URLs to use domain names
5. ✅ Added network testing support
6. ✅ Fixed CORS configuration to allow new domain ([backend/app/main.py:19-24](backend/app/main.py#L19-L24))
7. ✅ Fixed call link generation to use environment domain ([calendar/page.tsx:148-154](frontend/src/app/calendar/page.tsx#L148-L154))
8. ✅ Updated .env.local and next.config.js to use local Jitsi ([.env.local](frontend/.env.local), [next.config.js](frontend/next.config.js))

The platform should now work perfectly for local development and testing across your network!
