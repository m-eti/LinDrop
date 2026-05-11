import json
import secrets
import logging
from pathlib import Path

logger = logging.getLogger("LinDrop")

class Config:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "lindrop"
        self.config_file = self.config_dir / "config.json"
        self.default_config = {
            "copy_enabled": True,
            "file_enabled": True,
            "save_path": str(Path.home() / "Downloads" / "LinDrop"),
            "notifications_enabled": True,
            "port": 7631,
            "auth_token": secrets.token_hex(16)
        }
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.load()
    
    def load(self):
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
                
            # Ensure auth_token exists for older configs
            if "auth_token" not in self.data:
                self.data["auth_token"] = secrets.token_hex(16)
                self.save()
        else:
            self.data = self.default_config.copy()
            self.save()
        
        # Create save directory if it doesn't exist, safely supporting '~' logic
        Path(self.data["save_path"]).expanduser().mkdir(parents=True, exist_ok=True)
    
    def save(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4)
    
    def get(self, key):
        return self.data.get(key, self.default_config.get(key))
    
    def set(self, key, value):
        self.data[key] = value
        self.save()
