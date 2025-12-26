#!/bin/bash

# Setup local domain for Interpretation Platform
# This script adds the necessary entries to /etc/hosts

echo "Setting up local domain configuration..."
echo "This requires sudo privileges."
echo ""

# Check if entries already exist
if grep -q "interpretation-service.com" /etc/hosts; then
    echo "Entries already exist in /etc/hosts. Removing old entries..."
    sudo sed -i.bak '/interpretation-service.com/d' /etc/hosts
fi

# Add new entries
echo "Adding entries to /etc/hosts..."
echo "" | sudo tee -a /etc/hosts
echo "# Interpretation Platform Local Development" | sudo tee -a /etc/hosts
echo "127.0.0.1   app.interpretation-service.com" | sudo tee -a /etc/hosts
echo "127.0.0.1   meet.interpretation-service.com" | sudo tee -a /etc/hosts

# Flush DNS cache on macOS
echo ""
echo "Flushing DNS cache..."
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder 2>/dev/null

echo ""
echo "✓ Setup complete!"
echo ""
echo "Verify the configuration:"
echo "  ping app.interpretation-service.com"
echo "  ping meet.interpretation-service.com"
echo ""
echo "Both should resolve to 127.0.0.1"
