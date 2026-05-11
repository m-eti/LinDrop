"""
LinDrop - Local Linux server to share files and sync clipboard
"""
import sys
import argparse
import logging
import socketserver
from config import Config
from notifications import NotificationManager
from server import TransferService, ShareRequestHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("LinDrop")

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

def main():
    parser = argparse.ArgumentParser(description="LinDrop - Local Linux server to share files and sync clipboard")
    parser.add_argument("--init", action="store_true", help="Initialize config and exit")
    args = parser.parse_args()

    logger.info("=== LinDrop Starting ===")
    
    config = Config()
    
    if args.init:
        logger.info(f"Config initialized at {config.config_file}")
        logger.info(f"Auth Token: {config.get('auth_token')}")
        sys.exit(0)

    notification_manager = NotificationManager()
    transfer_service = TransferService(config, notification_manager)
    
    # Inject Dependencies
    ShareRequestHandler.transfer_service = transfer_service
    ShareRequestHandler.auth_token = config.get("auth_token")
    
    port = config.get("port")
    
    logger.info(f"Configuration loaded. Port: {port}")
    logger.info(f"IMPORTANT: Your Auth Token is -> {ShareRequestHandler.auth_token}")
    logger.info("Please configure this token in your client headers (X-Auth-Token).")
    
    try:
        with ThreadedTCPServer(("", port), ShareRequestHandler) as httpd:
            logger.info(f"LinDrop is running and listening on port {port}...")
            httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down LinDrop...")
        sys.exit(0)

if __name__ == "__main__":
    main()
