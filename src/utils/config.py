import json
from typing import Dict

# Default configurations for each media type
DEFAULT_CONFIG: Dict[str, Dict[str, list]] = {
    "anime": {
        "extensions": [".mp4", ".mkv", ".ts", ".avi", ".srt", ".ass"]
    },
    "movie": {
        "extensions": [".mp4", ".mkv", ".ts", ".avi"]
    },
    "book": {
        "extensions": [".pdf", ".epub", ".mobi", ".azw", ".txt"]
    }
}

def load_config(config_path: str) -> Dict:
    """Load configuration from a JSON file, falling back to defaults.

    Args:
        config_path (str): Path to the configuration file. Defaults to 'config.json'.

    Returns:
        Dict: Loaded configuration with defaults applied.
    """
    config = DEFAULT_CONFIG.copy()
    try:
        with open(config_path, "r") as f:
            user_config = json.load(f)
        # Update default config with user-provided values
        for key in user_config:
            if key in config:
                config[key].update(user_config[key])
            else:
                config[key] = user_config[key]
    except FileNotFoundError:
        print(f"Configuration file {config_path} not found. Using default configurations.")
    except json.JSONDecodeError:
        print(f"Error parsing {config_path}. Using default configurations.")
    return config