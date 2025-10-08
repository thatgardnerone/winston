"""Historical metrics storage using JSONL format"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class HistoryStore:
    """Simple JSONL-based time-series storage for metrics"""

    def __init__(self, history_file: Optional[Path] = None):
        """Initialize history store"""
        if history_file is None:
            history_file = Path.home() / ".winston_history.jsonl"
        self.history_file = history_file

    def append_snapshot(self, metrics: Dict[str, Any]) -> None:
        """
        Append a metrics snapshot to history

        Args:
            metrics: Dictionary of metrics to store
        """
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }

        # Append to JSONL file (create if doesn't exist)
        with open(self.history_file, 'a') as f:
            f.write(json.dumps(snapshot) + '\n')

    def prune_old_data(self, days: int = 30) -> int:
        """
        Remove snapshots older than specified days

        Args:
            days: Number of days to keep (default: 30)

        Returns:
            Number of snapshots removed
        """
        if not self.history_file.exists():
            return 0

        cutoff = datetime.now() - timedelta(days=days)
        kept_snapshots = []
        removed_count = 0

        # Read all snapshots
        with open(self.history_file, 'r') as f:
            for line in f:
                try:
                    snapshot = json.loads(line.strip())
                    timestamp = datetime.fromisoformat(snapshot['timestamp'])

                    if timestamp >= cutoff:
                        kept_snapshots.append(line.strip())
                    else:
                        removed_count += 1
                except (json.JSONDecodeError, KeyError, ValueError):
                    # Skip malformed lines
                    continue

        # Rewrite file with only kept snapshots
        with open(self.history_file, 'w') as f:
            for line in kept_snapshots:
                f.write(line + '\n')

        return removed_count

    def get_snapshot_count(self) -> int:
        """Get total number of snapshots in history"""
        if not self.history_file.exists():
            return 0

        count = 0
        with open(self.history_file, 'r') as f:
            for _ in f:
                count += 1
        return count
