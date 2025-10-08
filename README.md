# Homelab Brain 🧠

Winston for your homelab - Natural language AI assistant powered by local LLMs.

## Features

- **Natural Language Interface**: Ask questions about your homelab in plain English
- **Smart Context Gathering**: Only fetches relevant metrics based on your question
- **Auto-WakeOnLAN**: Automatically wakes your GPU workstation when needed
- **MOTD Integration**: Hourly AI summaries appear in your login message
- **Health Monitoring**: Integrates with systemd and Docker health checks
- **Privacy First**: All AI inference runs locally on your own hardware

## Quick Start

### Prerequisites

- Python 3.12+
- [Ollama](https://ollama.com) running on a GPU workstation
- WakeOnLAN configured for your GPU workstation
- SSH access to your GPU workstation

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/homelab-brain.git
cd homelab-brain
```

2. Create and activate virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -e ".[dev]"
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Add to PATH:
```bash
mkdir -p ~/.local/bin
ln -sf $(pwd)/.venv/bin/lab ~/.local/bin/lab
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

### Usage

Ask Winston questions:
```bash
lab ask "How much memory is available?"
lab ask "What's my CPU usage?"
lab ask "Are there any Docker containers running?"
lab status
```

### MOTD Integration

Add Winston's AI summaries to your login message:

1. Create MOTD script:
```bash
sudo tee /etc/update-motd.d/95-winston <<'SCRIPT'
#!/bin/sh
SUMMARY_FILE="/home/$(whoami)/.winston_summary"
if [ -f "$SUMMARY_FILE" ]; then
    echo -n "✨ "
    cat "$SUMMARY_FILE"
    echo
fi
SCRIPT
sudo chmod +x /etc/update-motd.d/95-winston
```

2. Set up hourly cron job:
```bash
(crontab -l 2>/dev/null; echo "0 * * * * cd $HOME/code/homelab-brain && .venv/bin/python3 -m homelab_brain.motd_summary >> $HOME/.winston.log 2>&1") | crontab -
```

## Configuration

All configuration is done via environment variables in `.env`:

- `OLLAMA_HOST`: Ollama server URL (default: http://gpu-workstation.local:11434)
- `OLLAMA_MODEL`: Model to use (default: gemma3:4b)
- `TGOML_MAC`: MAC address for WakeOnLAN
- `TGOML_HOST`: Hostname of GPU workstation
- `HEALTH_CHECK_PATH`: Path to homelab-health checker script

## Architecture

```
┌─────────────┐
│   CLI/Cron  │  User asks questions or cron runs
└──────┬──────┘
       │
┌──────▼──────┐
│    Brain    │  Orchestrates everything
└──────┬──────┘
       │
       ├──────────┐
       │          │
┌──────▼──────┐  ┌▼───────────────┐
│   Context   │  │ OllamaClient   │
│   Gatherer  │  │ + WakeOnLAN    │
└─────────────┘  └────────────────┘
```

- **Brain**: Core orchestrator, decides what context to gather
- **SystemContext**: Gathers CPU, memory, disk, Docker, health metrics
- **OllamaClient**: Manages connection to Ollama, auto-wakes GPU workstation
- **CLI**: User-friendly command-line interface

## Current Work: Historical Trends

We're building historical trend tracking using a lean, iterative approach:

### Iteration 1: Simple Time-Series Storage ✅ COMPLETE
**Goal:** Store metrics over time without over-engineering

- ✅ Extend JSON approach: `~/.winston_history.jsonl` (JSON Lines format)
- ✅ Each line = one snapshot with timestamp
- ✅ Keep last 30 days (auto-prune old data)
- ✅ No querying yet, just collection

**Result:** Background data collection working! Metrics stored every hour via cron.

### Iteration 2: Basic Trend Detection ✅ COMPLETE
**Goal:** Detect simple patterns

- ✅ Read last 7 days of history
- ✅ Calculate averages (issues, containers - local & remote, services)
- ✅ Compare current to 7-day average
- ✅ Mention if significantly different (>20% change)
- ✅ Pass trend insights to Winston's prompt

**Result:** Winston now mentions significant trends! "Tgoml containers up 33%" or "Issues down 50% from weekly average"

### Iteration 3: SQLite Migration (FUTURE)
**Goal:** Efficient querying for richer insights (only when JSONL gets unwieldy)

- Migrate to SQLite with simple schema
- Add queries for weekly/monthly trends
- Keep it simple - no EAV until we need it

### Iteration 4: Rich Insights (FUTURE)
**Goal:** Smarter trend analysis

- Week-over-week comparisons
- Anomaly detection (spikes/dips)
- Winston mentions most notable trend

**Example output:** "Tgoml has been awake 40% more this week - burning through those tokens?"

### Iteration 5: EAV Model (MAYBE)
**Goal:** Flexible schema for arbitrary metrics (only if needed)

- Entity-Attribute-Value schema for custom metrics
- Query language for trends
- Decision: Do we need this complexity?

### Key Metrics to Track
- CPU usage (percent, load average)
- Memory usage (percent, GB free)
- Disk usage (percent, GB free)
- Issue count (from health checks)
- Container counts (local + remote)
- Host reachability (tgoml wake/sleep cycles)

## Development

Run tests:
```bash
pytest
pytest -v  # verbose
pytest tests/test_brain.py  # specific test
```

## License

MIT

## Credits

Inspired by Winston from Dan Brown's *Origin* - your personal AI assistant for homelab management.
