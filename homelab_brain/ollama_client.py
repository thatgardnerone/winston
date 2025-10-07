"""OllamaClient for interacting with Ollama API"""
import ollama
import subprocess
import time
from typing import Optional
from config import config


class OllamaClient:
    """Client for communicating with Ollama API"""

    def __init__(self):
        self.host = config("ollama.host")
        self.model = config("ollama.model")
        self.temperature = config("ollama.temperature")
        self.timeout = config("ollama.timeout")

        # WakeOnLAN config
        self.tgoml_mac = config("homelab.tgoml.mac_address")
        self.tgoml_hostname = config("homelab.tgoml.hostname")
        self.wake_wait_seconds = config("homelab.tgoml.wake_wait_seconds")

        # Create ollama client
        self.client = ollama.Client(host=self.host)

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """
        Generate a response from Ollama

        Args:
            prompt: The user prompt/question
            system: Optional system context/instructions

        Returns:
            Generated text response
        """
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat(
                model=self.model,
                messages=messages,
                options={"temperature": self.temperature},
            )

            return response["message"]["content"].strip()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Ollama: {e}")

    def wake_tgoml(self) -> bool:
        """
        Wake tgoml using WakeOnLAN

        Returns:
            True if tgoml woke up successfully, False otherwise
        """
        try:
            # Send WOL packet
            subprocess.run(
                ['wakeonlan', self.tgoml_mac],
                capture_output=True,
                check=True,
                timeout=5
            )

            # Wait for it to wake up
            print(f"⏰ Waking tgoml... (waiting {self.wake_wait_seconds}s)")
            time.sleep(self.wake_wait_seconds)

            # Verify it's up by pinging
            result = subprocess.run(
                ['ping', '-c', '2', '-W', '2', self.tgoml_hostname],
                capture_output=True,
                timeout=5
            )

            if result.returncode != 0:
                return False

            # SSH in to trigger Docker Desktop to start
            print("🐳 Triggering Docker startup...")
            import getpass
            username = getpass.getuser()
            subprocess.run(
                ['ssh', f'{username}@{self.tgoml_hostname}', 'echo "Docker check"'],
                capture_output=True,
                timeout=10
            )

            # Give Docker a moment to start
            time.sleep(10)

            return True

        except Exception as e:
            print(f"❌ Failed to wake tgoml: {e}")
            return False

    def is_available(self) -> bool:
        """Check if Ollama is reachable"""
        try:
            self.client.list()
            return True
        except:
            return False

    def ensure_available(self) -> bool:
        """
        Ensure Ollama is available, wake tgoml if needed

        Returns:
            True if Ollama is available (or was successfully woken)
        """
        # First check if already available
        if self.is_available():
            return True

        # Not available - try waking tgoml
        print("🔌 tgoml appears to be asleep...")
        if self.wake_tgoml():
            # Check again after waking
            return self.is_available()

        return False
