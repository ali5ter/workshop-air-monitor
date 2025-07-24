#!/usr/bin/env bash
# @file: start_env_monitor_service.sh
# @brief: Script to start the environment monitor systemd service.
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>
# @note: This script is intended for Debian-based systems (e.g., Raspberry Pi OS).

[[ -n $DEBUG ]] && set -x
set -eou pipefail

# Create systemd Unit file for the environment monitor service
echo "📄 Creating systemd service file for environment monitor..."
cp env_monitor.service.template /etc/systemd/system/env_monitor.service

# Reload systemd configuration to ensure the service file is recognized
echo "🔄 Reloading systemd configuration..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

# Start the environment monitor service
echo "🚀 Starting environment monitor service..."
sudo systemctl enable env_monitor.service
sudo systemctl start env_monitor.service

# Check the status of the service to confirm it's running
systemctl status env_monitor.service
if systemctl is-active --quiet env_monitor.service; then
    echo "✅ Environment monitor service is running successfully."
else
    echo "❌ Failed to start environment monitor service."
    exit 1
fi

# Display the last 50 lines of the service log for debugging
echo "📜 Displaying the last 50 lines of the service log for debugging..."
journalctl -u env_monitor.service -n 50 --no-pager

echo "🔚 Environment monitor service setup complete."
echo "You can check the service status with 'systemctl status env_monitor.service' and view logs with 'journalctl -u env_monitor.service'."
echo "To stop the service, use 'sudo systemctl stop env_monitor.service'."
echo "To disable the service from starting on boot, use 'sudo systemctl disable env_monitor.service'."
echo "To restart the service, use 'sudo systemctl restart env_monitor.service'."