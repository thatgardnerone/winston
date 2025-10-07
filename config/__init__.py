import os
from typing import Any

class Config:
    """Laravel-style configuration manager with auto-discovery"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.config_dict = {}
            cls._instance.load_config()
        return cls._instance

    def load_config(self):
        """Auto-discover config files in the config directory"""
        config_dir = os.path.dirname(__file__)

        for filename in os.listdir(config_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]
                module = __import__(f'config.{module_name}', fromlist=['config'])
                self.config_dict[module_name] = module.config

    @staticmethod
    def get(path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        Example: config.get("ollama.host")
        """
        config_instance = Config()
        keys = path.split('.')

        current_level = config_instance.config_dict

        # Traverse the dictionary
        for key in keys[:-1]:
            if key not in current_level or not isinstance(current_level[key], dict):
                return default
            current_level = current_level[key]

        final_key = keys[-1]
        return current_level.get(final_key, default)

    def reload(self):
        """Reload configuration (useful for testing)"""
        self._instance = None
        Config()


def config(path: str, default: Any = None) -> Any:
    """
    Simple helper function for getting config values

    Usage:
        from config import config
        host = config("ollama.host")
    """
    return Config.get(path, default)
