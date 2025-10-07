"""
Test WakeOnLAN functionality for waking tgoml

We want to ensure we can wake the GPU workstation before sending queries
"""

import pytest
import subprocess
from unittest.mock import patch, MagicMock


class TestWakeOnLAN:
    """Test waking tgoml workstation"""

    def test_can_send_wol_packet(self):
        """
        Verify we can send WakeOnLAN packet
        Uses wakeonlan command
        """
        from config import config
        mac = config("homelab.tgoml.mac_address")

        # Actually send the packet (safe - just wakes machine)
        result = subprocess.run(
            ["wakeonlan", mac],
            capture_output=True,
            text=True,
            timeout=5
        )

        assert result.returncode == 0
        assert "Sending magic packet" in result.stdout or "Sending" in result.stdout

    @patch('subprocess.run')
    def test_wol_command_format(self, mock_run):
        """Test the WOL command is formatted correctly"""
        mock_run.return_value = MagicMock(returncode=0, stdout="Sending magic packet")

        mac = "AA:BB:CC:DD:EE:FF"
        result = subprocess.run(["wakeonlan", mac], capture_output=True, text=True)

        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args == ["wakeonlan", mac]

    def test_can_check_if_host_is_awake(self):
        """
        Test pinging GPU workstation to see if it's awake
        """
        from config import config
        hostname = config("homelab.tgoml.hostname")

        # Ping with 1 packet, 2 second timeout
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", hostname],
            capture_output=True,
            text=True,
            timeout=5
        )

        # We don't assert success (machine might be asleep)
        # Just verify the command works
        assert result.returncode in [0, 1]  # 0 = success, 1 = no response


class TestWakeSequence:
    """Test the full wake sequence"""

    @pytest.mark.skip(reason="Will implement when we build OllamaClient")
    def test_wake_and_wait_sequence(self):
        """
        Full sequence:
        1. Check if awake
        2. If not, send WOL
        3. Wait for host to respond
        4. Connect to Ollama
        """
        pass
