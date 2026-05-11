#!/usr/bin/env bash
set -e

echo "Installing LinDrop..."

INSTALL_DIR="$HOME/.local/share/lindrop"
BIN_DIR="$HOME/.local/bin"
SYSTEMD_DIR="$HOME/.config/systemd/user"

# Check dependencies
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required but not installed."
    exit 1
fi

if ! command -v notify-send &> /dev/null; then
    echo "Warning: notify-send (libnotify-bin) is missing. Notifications won't work."
fi

# Prepare directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$SYSTEMD_DIR"

# Copy project files
echo "Copying files to $INSTALL_DIR"
cp *.py "$INSTALL_DIR/"
cp lindrop_config.json.example "$INSTALL_DIR/"

# Create CLI wrapper
echo "Creating executable wrapper at $BIN_DIR/lindrop"
cat << EOF > "$BIN_DIR/lindrop"
#!/usr/bin/env bash
exec python3 "$INSTALL_DIR/main.py" "\$@"
EOF
chmod +x "$BIN_DIR/lindrop"

# Install and enable systemd service
echo "Setting up systemd service..."
cp lindrop.service "$SYSTEMD_DIR/"
systemctl --user daemon-reload
systemctl --user enable --now lindrop.service

echo "LinDrop installed successfully!"
echo "You can check the logs anytime using: journalctl --user -fu lindrop"

# Generate initial config to print token to user
"$BIN_DIR/lindrop" --init