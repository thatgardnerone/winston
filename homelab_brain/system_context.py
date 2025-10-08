"""SystemContext - Gather homelab metrics and state"""
import psutil
import subprocess
import json
import re
from typing import Dict, Any, List, Optional
from config import config


class SystemContext:
    """Gathers system metrics and context for AI responses"""

    def gather_cpu(self) -> Dict[str, Any]:
        """Get CPU usage and stats"""
        return {
            "percent": psutil.cpu_percent(interval=0.1),
            "count": psutil.cpu_count(),
            "load_avg": psutil.getloadavg(),
        }

    def gather_memory(self) -> Dict[str, Any]:
        """Get memory usage"""
        mem = psutil.virtual_memory()
        return {
            "total_gb": round(mem.total / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2),
            "percent": mem.percent,
        }

    def gather_disk(self) -> Dict[str, Any]:
        """Get disk usage for root partition"""
        disk = psutil.disk_usage('/')
        return {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent": disk.percent,
        }

    def gather_docker(self) -> Dict[str, Any]:
        """Get Docker container status"""
        try:
            result = subprocess.run(
                ['docker', 'ps', '--format', '{{json .}}'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return {"error": "Docker not accessible"}

            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    container = json.loads(line)
                    containers.append({
                        "name": container.get("Names", ""),
                        "status": container.get("Status", ""),
                        "image": container.get("Image", ""),
                    })

            return {
                "running": len(containers),
                "containers": containers,
            }
        except Exception as e:
            return {"error": str(e)}

    def gather_remote_host(self, hostname: Optional[str] = None) -> Dict[str, Any]:
        """Get Docker container status from remote host via SSH"""
        if not hostname:
            hostname = config("homelab.tgoml.hostname")

        try:
            # Try to get Docker container info via SSH
            result = subprocess.run(
                ['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=3',
                 f'jamie@{hostname}',
                 'docker ps --format "{{.Names}}\t{{.State}}\t{{.Status}}"'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return {"error": "Host unreachable or SSH failed", "reachable": False}

            containers = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split('\t')
                if len(parts) >= 2:
                    containers.append({
                        "name": parts[0],
                        "state": parts[1] if len(parts) > 1 else "unknown",
                        "status": parts[2] if len(parts) > 2 else "unknown",
                    })

            return {
                "hostname": hostname,
                "reachable": True,
                "container_count": len(containers),
                "containers": containers,
            }
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
            return {"error": str(e), "reachable": False}

    def gather_health(self) -> Dict[str, Any]:
        """Get health check status from homelab-health"""
        try:
            health_script = config("homelab.server.health_check_path")
            result = subprocess.run(
                [health_script],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Strip ANSI color codes and decode escape sequences
            output = re.sub(r'\x1b\[[0-9;]+m', '', result.stdout)
            output = output.replace('\\x2d', '-').replace('\\x2ddns\\x2d', '-dns-')

            issues = []

            # Look for issue lines (✗, ⚠, ℹ symbols)
            # Pattern: symbol category: name - message
            for line in output.split('\n'):
                if any(symbol in line for symbol in ['✗', '⚠', 'ℹ']):
                    # Extract parts: "✗ systemd: snap-certbot-dns-cloudflare-4697.mount - service failed"
                    match = re.match(r'[✗⚠ℹ]\s+(\w+):\s+(.+?)\s+-\s+(.+)', line.strip())
                    if match:
                        issues.append({
                            "category": match.group(1),
                            "name": match.group(2).strip(),
                            "message": match.group(3).strip(),
                        })

            # Extract summary - handles both formats:
            # "27 services • 3 containers • 1 issue" (when issues exist)
            # "27 services • 3 containers running" (when no issues)
            summary_match = re.search(r'(\d+)\s+services\s+•\s+(\d+)\s+containers', output)
            issue_match = re.search(r'(\d+)\s+issue', output)

            return {
                "total_services": int(summary_match.group(1)) if summary_match else 0,
                "total_containers": int(summary_match.group(2)) if summary_match else 0,
                "issue_count": int(issue_match.group(1)) if issue_match else len(issues),
                "issues": issues,
            }
        except Exception as e:
            return {"error": str(e)}

    def gather_all(self) -> Dict[str, Any]:
        """Gather all available context"""
        return {
            "cpu": self.gather_cpu(),
            "memory": self.gather_memory(),
            "disk": self.gather_disk(),
            "docker": self.gather_docker(),
            "health": self.gather_health(),
        }

    def gather_relevant(self, query: str) -> Dict[str, Any]:
        """
        Smart context gathering - only fetch what's relevant to the query

        This saves time and reduces noise in the AI context
        """
        query_lower = query.lower()
        context = {}

        # Keywords that trigger specific context gathering
        if any(word in query_lower for word in ['cpu', 'processor', 'load', 'performance']):
            context['cpu'] = self.gather_cpu()

        if any(word in query_lower for word in ['memory', 'ram', 'mem']):
            context['memory'] = self.gather_memory()

        if any(word in query_lower for word in ['disk', 'storage', 'space', 'drive']):
            context['disk'] = self.gather_disk()

        if any(word in query_lower for word in ['docker', 'container', 'service']):
            context['docker'] = self.gather_docker()

        # Always include health status for summaries or when explicitly requested
        if any(word in query_lower for word in ['summary', 'status', 'health', 'issue', 'problem', 'error']):
            context['health'] = self.gather_health()
            # Also check remote host for summaries
            context['remote_host'] = self.gather_remote_host()

        # Check for remote host/tgoml keywords
        if any(word in query_lower for word in ['tgoml', 'remote', 'gpu', 'workstation']):
            context['remote_host'] = self.gather_remote_host()

        # If no specific context matched, gather a summary
        if not context:
            context = {
                'cpu': self.gather_cpu(),
                'memory': self.gather_memory(),
                'health': self.gather_health(),
                'remote_host': self.gather_remote_host(),
            }

        return context

    def format_for_prompt(self, context: Dict[str, Any]) -> str:
        """Format context into a string suitable for AI prompt"""
        lines = ["Current system state:"]

        if 'cpu' in context:
            cpu = context['cpu']
            lines.append(f"- CPU: {cpu['percent']}% ({cpu['count']} cores, load: {cpu['load_avg']})")

        if 'memory' in context:
            mem = context['memory']
            lines.append(f"- Memory: {mem['percent']}% used ({mem['available_gb']}/{mem['total_gb']} GB available)")

        if 'disk' in context:
            disk = context['disk']
            lines.append(f"- Disk: {disk['percent']}% used ({disk['free_gb']}/{disk['total_gb']} GB free)")

        if 'docker' in context:
            docker = context['docker']
            if 'error' not in docker:
                lines.append(f"- Docker: {docker['running']} containers running")
                for c in docker.get('containers', [])[:5]:  # Limit to first 5
                    lines.append(f"  • {c['name']}: {c['status']}")

        if 'health' in context:
            health = context['health']
            if 'error' not in health:
                lines.append(f"- Health: {health['total_services']} services, {health['total_containers']} containers, {health['issue_count']} issues")
                if health['issues']:
                    lines.append("  Issues found:")
                    for issue in health['issues']:
                        lines.append(f"    • {issue['category']}: {issue['name']} - {issue['message']}")

        if 'remote_host' in context:
            remote = context['remote_host']
            if remote.get('reachable'):
                hostname = remote.get('hostname', 'remote host')
                container_count = remote.get('container_count', 0)
                lines.append(f"- Remote host ({hostname}): {container_count} containers running")
                for c in remote.get('containers', [])[:5]:  # Limit to first 5
                    lines.append(f"  • {c['name']}: {c['status']}")
            else:
                lines.append(f"- Remote host: unreachable or sleeping")

        return '\n'.join(lines)
