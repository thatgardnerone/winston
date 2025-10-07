import os
from dotenv import load_dotenv

load_dotenv()

config = {
    "host": os.getenv("OLLAMA_HOST", "http://gpu-workstation.local:11434"),
    "model": os.getenv("OLLAMA_MODEL", "gemma3:4b"),
    "temperature": float(os.getenv("OLLAMA_TEMPERATURE", "0.3")),
    "timeout": int(os.getenv("OLLAMA_TIMEOUT", "30")),  # seconds
}
