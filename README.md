# LinDrop

LinDrop is a lightweight, local Linux server designed to seamlessly share files and sync your clipboard from Apple devices (iOS/macOS) to your Linux machine. It runs securely on your local network, requiring an authentication token to accept incoming transfers.

## Features

- **Clipboard Sync**: Instantly sync copied text and files from your Apple devices directly to your Linux machine's clipboard.
- **File Transfers**: Send photos, videos, and documents straight to your Linux `~/Downloads/LinDrop` folder.
- **Native Notifications**: Get instant desktop notifications when a file or text is received.
- **Wayland & X11 Support**: Automatically detects and uses `wl-copy` or `xclip` for clipboard management.
- **Secure**: Protected by a randomly generated authentication token (`X-Auth-Token`).
- **Systemd Integration**: Runs quietly in the background as a user systemd service.

## Prerequisites

Ensure you have the following installed on your Linux machine:
- `python3`
- `wl-clipboard` (for Wayland) OR `xclip` (for X11)
- `libnotify-bin` (for native desktop notifications via `notify-send`)

## Installation

1. Clone the repository (or download the files):
   ```bash
   git clone https://github.com/m-eti/LinDrop.git
   cd LinDrop
   ```
2. Run the installation script:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
3. During installation, your **Auth Token** will be printed to the terminal. Save this! You will need it to configure your client.

## Client Setup

To send data to LinDrop, you can use a companion client or Apple Shortcut:

[**Download the LinDrop Apple Shortcut here**](https://www.icloud.com/shortcuts/4cb2d94fc2014236bb72935269d43c8a)

### Configuring the Client
1. Download and install the client or shortcut using the link above.
2. Edit the client settings on your device.
3. Update the **Server IP** to match your Linux machine's local IP address (e.g., `192.168.1.50`) and ensure the port is set to `7631`.
4. Update the **`X-Auth-Token`** header in the client's network action with the token generated during installation.

## Configuration

LinDrop's configuration is stored at `~/.config/lindrop/config.json`. You can modify it to suit your needs:

```json
{
    "copy_enabled": true,
    "file_enabled": true,
    "save_path": "/home/youruser/Downloads/LinDrop",
    "notifications_enabled": true,
    "port": 7631,
    "auth_token": "your_secure_hex_token"
}
```

## Service Management

LinDrop runs as a background `systemd` user service. You can manage it with the following commands:

- **Check Status**: `systemctl --user status lindrop.service`
- **Restart Service**: `systemctl --user restart lindrop.service`
- **Stop Service**: `systemctl --user stop lindrop.service`
- **View Logs**: `journalctl --user -fu lindrop`

## Uninstallation

If you wish to remove LinDrop from your system, simply run the included uninstall script:

```bash
chmod +x uninstall.sh
./uninstall.sh
```