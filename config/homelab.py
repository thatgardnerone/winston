import os
from dotenv import load_dotenv

load_dotenv()

config = {
    "server": {
        "name": os.getenv("SERVER_NAME", "homelab.local"),
        "health_check_path": os.getenv(
            "HEALTH_CHECK_PATH",
            f"/home/{os.getenv('USER')}/code/homelab-health/health_check.py"
        ),
    },
    "tgoml": {
        "mac_address": os.getenv("TGOML_MAC", "00:00:00:00:00:00"),
        "hostname": os.getenv("TGOML_HOST", "gpu-workstation.local"),
        "wake_wait_seconds": int(os.getenv("WAKE_WAIT", "30")),
        "ping_timeout": int(os.getenv("PING_TIMEOUT", "2")),
    },
    "storage": {
        "database_path": os.getenv("DB_PATH", f"/home/{os.getenv('USER')}/code/homelab-brain/brain.db"),
    }
}
