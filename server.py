import http.server
import json
import subprocess
from pathlib import Path
from datetime import datetime
import time
import email
import base64
import logging

logger = logging.getLogger("LinDrop")

class TransferService:
    def __init__(self, config, notification_manager):
        self.config = config
        self.notifier = notification_manager

    def copy_to_clipboard(self, text: str) -> bool:
        if not self.config.get('copy_enabled'):
            return False
        try:
            if self.config.get('wayland_display'):
                subprocess.run(['wl-copy'], input=text.encode('utf-8'), check=True)
            else:
                subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode('utf-8'), check=True)
            return True
        except Exception as e:
            logger.error(f"Clipboard error: {e}")
            return False

    def save_file(self, filename: str, file_data: bytes) -> str:
        if not self.config.get('file_enabled'):
            return None
            
        save_dir = Path(self.config.get('save_path')).expanduser()
        save_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        file_path = save_dir / safe_filename
        
        with open(file_path, 'wb') as f:
            f.write(file_data)
        return str(file_path)

    def handle_payload(self, device_name, message, filename, file_data):
        copied = False
        saved_path = None
        
        if message:
            copied = self.copy_to_clipboard(message)
            if copied and self.config.get('notifications_enabled'):
                self.notifier.show("LinDrop", f"Text copied from {device_name}")
                
        if file_data and filename:
            try:
                saved_path = self.save_file(filename, file_data)
                if saved_path and self.config.get('notifications_enabled'):
                    self.notifier.show("LinDrop", f"File '{filename}' received from {device_name}", is_file=True)
            except Exception as e:
                logger.error(f"File save error: {e}")
                raise e
                
        return copied, saved_path

class ShareRequestHandler(http.server.BaseHTTPRequestHandler):
    transfer_service: TransferService = None
    auth_token: str = None

    def send_response_custom(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def log_message(self, format, *args):
        logger.info(f"{self.client_address[0]} - {format%args}")

    def do_POST(self):
        if self.path != '/share':
            return self.send_response_custom(404, {"error": "Not found"})

        auth_token = self.headers.get('X-Auth-Token')
        if auth_token != self.auth_token:
            logger.warning(f"Unauthorized request from {self.client_address[0]}")
            return self.send_response_custom(401, {"error": "Unauthorized: Invalid or missing X-Auth-Token header"})

        device_name = self.headers.get('X-Device-Name', 'Unknown Device')
        content_length = int(self.headers.get('Content-Length', 0))
        content_type = self.headers.get('Content-Type', '')

        body = self.rfile.read(content_length)

        message = None
        file_data = None
        filename = None

        try:
            if content_type.startswith('multipart/'):
                headers = f"Content-Type: {content_type}\r\n\r\n".encode('utf-8')
                msg = email.message_from_bytes(headers + body)
                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart': continue
                    filename_part = part.get_filename()
                    content_disp = part.get('Content-Disposition', '')
                    if filename_part:
                        file_data = part.get_payload(decode=True)
                        filename = filename_part
                    elif 'name="message"' in content_disp:
                        message = part.get_payload(decode=True).decode('utf-8', errors='ignore')
            elif 'application/json' in content_type:
                data = json.loads(body.decode('utf-8'))
                message = data.get('message')
                if 'file_data' in data and 'file_name' in data:
                    file_data = base64.b64decode(data['file_data'])
                    filename = data['file_name']
            else:
                file_data = body
                ext = content_type.split('/')[-1] if '/' in content_type else 'bin'
                filename = f"file_{int(time.time())}.{ext}"

            copied, saved_path = self.transfer_service.handle_payload(device_name, message, filename, file_data)
            return self.send_response_custom(200, {
                "message_copied": copied,
                "file_saved": bool(saved_path),
                "file_path": saved_path
            })
        except Exception as e:
            logger.error(f"Error processing POST request: {e}")
            return self.send_response_custom(500, {"error": str(e)})
