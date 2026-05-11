#!/usr/bin/env bash
set -e

echo "Uninstalling LinDrop..."

INSTALL_DIR="$HOME/.local/share/lindrop"
BIN_FILE="$HOME/.local/bin/lindrop"
SYSTEMD_FILE="$HOME/.config/systemd/user/lindrop.service"
CONFIG_DIR="$HOME/.config/lindrop"

# Stop and disable service if it exists
if systemctl --user is-active --quiet lindrop.service 2>/dev/null; then
    echo "Stopping lindrop service..."
    systemctl --user stop lindrop.service
fi

if systemctl --user is-enabled --quiet lindrop.service 2>/dev/null; then
    echo "Disabling lindrop service..."
    systemctl --user disable lindrop.service
fi

# Remove application files
echo "Removing application files..."
rm -rf "$INSTALL_DIR"
rm -f "$BIN_FILE"
rm -f "$SYSTEMD_FILE"

echo "Reloading systemd daemon..."
systemctl --user daemon-reload

read -p "Do you want to remove the configuration files and auth token? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$CONFIG_DIR"
    echo "Configuration removed."
fi

echo "LinDrop has been uninstalled."