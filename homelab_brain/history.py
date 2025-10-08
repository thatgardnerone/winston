"""Historical metrics storage using JSONL format"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List


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

    def read_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Read snapshots from the last N days

        Args:
            days: Number of days to read (default: 7)

        Returns:
            List of snapshots (newest first)
        """
        if not self.history_file.exists():
            return []

        cutoff = datetime.now() - timedelta(days=days)
        snapshots = []

        with open(self.history_file, 'r') as f:
            for line in f:
                try:
                    snapshot = json.loads(line.strip())
                    timestamp = datetime.fromisoformat(snapshot['timestamp'])

                    if timestamp >= cutoff:
                        snapshots.append(snapshot)
                except (json.JSONDecodeError, KeyError, ValueError):
                    # Skip malformed lines
                    continue

        # Return newest first
        snapshots.reverse()
        return snapshots


class TrendAnalyzer:
    """Analyze historical trends from stored snapshots"""

    def __init__(self, history_store: HistoryStore):
        """Initialize trend analyzer with a history store"""
        self.history = history_store

    def calculate_averages(self, days: int = 7) -> Dict[str, float]:
        """
        Calculate average values for key metrics over N days

        Args:
            days: Number of days to analyze (default: 7)

        Returns:
            Dictionary of metric averages
        """
        snapshots = self.history.read_history(days=days)

        if not snapshots:
            return {}

        # Accumulate values
        totals = {
            'issue_count': 0,
            'local_containers': 0,
            'remote_containers': 0,
            'services': 0,
        }
        counts = {key: 0 for key in totals.keys()}

        for snapshot in snapshots:
            metrics = snapshot.get('metrics', {})
            health = metrics.get('health', {})
            remote = metrics.get('remote_host', {})

            # Count issues
            if 'issue_count' in health:
                totals['issue_count'] += health['issue_count']
                counts['issue_count'] += 1

            # Count local containers
            if 'total_containers' in health:
                totals['local_containers'] += health['total_containers']
                counts['local_containers'] += 1

            # Count services
            if 'total_services' in health:
                totals['services'] += health['total_services']
                counts['services'] += 1

            # Count remote containers (only when reachable)
            if remote.get('reachable') and 'container_count' in remote:
                totals['remote_containers'] += remote['container_count']
                counts['remote_containers'] += 1

        # Calculate averages
        averages = {}
        for key in totals:
            if counts[key] > 0:
                averages[key] = totals[key] / counts[key]

        return averages

    def detect_significant_changes(self, current_metrics: Dict[str, Any], threshold: float = 0.2) -> List[str]:
        """
        Detect significant changes from historical averages

        Args:
            current_metrics: Current metric values
            threshold: Percentage change to consider significant (default: 0.2 = 20%)

        Returns:
            List of human-readable change descriptions
        """
        averages = self.calculate_averages(days=7)

        if not averages:
            return []  # Not enough history yet

        changes = []
        health = current_metrics.get('health', {})
        remote = current_metrics.get('remote_host', {})

        # Check issue count
        current_issues = health.get('issue_count', 0)
        avg_issues = averages.get('issue_count', 0)
        if avg_issues > 0 and abs(current_issues - avg_issues) / avg_issues > threshold:
            if current_issues > avg_issues:
                changes.append(f"Issues up {int((current_issues - avg_issues) / avg_issues * 100)}% from weekly average")
            else:
                changes.append(f"Issues down {int((avg_issues - current_issues) / avg_issues * 100)}% from weekly average")

        # Check local containers
        current_local = health.get('total_containers', 0)
        avg_local = averages.get('local_containers', 0)
        if avg_local > 0 and abs(current_local - avg_local) / avg_local > threshold:
            if current_local > avg_local:
                changes.append(f"Local containers up {int((current_local - avg_local) / avg_local * 100)}%")
            else:
                changes.append(f"Local containers down {int((avg_local - current_local) / avg_local * 100)}%")

        # Check remote containers (only if currently reachable)
        if remote.get('reachable'):
            current_remote = remote.get('container_count', 0)
            avg_remote = averages.get('remote_containers', 0)
            if avg_remote > 0 and abs(current_remote - avg_remote) / avg_remote > threshold:
                if current_remote > avg_remote:
                    changes.append(f"Tgoml containers up {int((current_remote - avg_remote) / avg_remote * 100)}%")
                else:
                    changes.append(f"Tgoml containers down {int((avg_remote - current_remote) / avg_remote * 100)}%")

        return changes
