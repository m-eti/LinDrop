import subprocess
import logging

logger = logging.getLogger("LinDrop")

class NotificationManager:
    def __init__(self):
        logger.info("Notification system initialized (notify-send)")

    def show(self, title, message, duration=5000, is_file=False):
        """Shows notification using notify-send (native Linux/GNOME)"""
        # Pick an icon based on whether a file is being transferred or text is copied
        icon = "document-save" if is_file else "edit-copy"

        try:
            cmd = ["notify-send", "-a", "LinDrop", "-i", icon, title, message, "-t", str(duration)]
            
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
                
            logger.debug(f"Notification sent: {title} - {message}")
        except FileNotFoundError:
            logger.warning("`notify-send` command not found. Notifications will not be shown.")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
