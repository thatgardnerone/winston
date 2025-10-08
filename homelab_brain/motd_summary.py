#!/usr/bin/env python3
"""
Generate AI summary for MOTD

This script:
1. Gathers system context from lab01
2. Wakes tgoml if needed
3. Asks Winston for a summary
4. Saves to a file for MOTD to display
"""
import sys
import os
import json
from pathlib import Path
from datetime import datetime
from homelab_brain.brain import Brain


def load_previous_state():
    """Load previous summary state for change detection"""
    state_file = Path.home() / ".winston_state.json"
    if state_file.exists():
        try:
            return json.loads(state_file.read_text())
        except:
            return None
    return None


def save_current_state(context):
    """Save current state for next run comparison"""
    state_file = Path.home() / ".winston_state.json"
    health = context.get('health', {})
    state = {
        'services': health.get('total_services', 0),
        'containers': health.get('total_containers', 0),
        'issues': health.get('issue_count', 0),
        'timestamp': datetime.now().isoformat()
    }
    state_file.write_text(json.dumps(state, indent=2))


def detect_changes(previous, current_context):
    """Detect changes between previous and current state"""
    if not previous:
        return None

    health = current_context.get('health', {})
    current = {
        'services': health.get('total_services', 0),
        'containers': health.get('total_containers', 0),
        'issues': health.get('issue_count', 0)
    }

    changes = []
    if current['issues'] < previous['issues']:
        resolved = previous['issues'] - current['issues']
        changes.append(f"{resolved} issue(s) resolved since last check")
    elif current['issues'] > previous['issues']:
        new = current['issues'] - previous['issues']
        changes.append(f"{new} new issue(s) detected")

    if current['services'] != previous['services']:
        diff = current['services'] - previous['services']
        changes.append(f"{abs(diff)} service(s) {'started' if diff > 0 else 'stopped'}")

    if current['containers'] != previous['containers']:
        diff = current['containers'] - previous['containers']
        changes.append(f"{abs(diff)} container(s) {'started' if diff > 0 else 'stopped'}")

    return changes if changes else None


def generate_summary():
    """Generate Winston's summary and save it"""
    brain = Brain()

    # Get current user and time context
    username = os.getenv('USER', 'there')
    hour = datetime.now().hour
    if hour < 12:
        greeting = "morning"
    elif hour < 18:
        greeting = "afternoon"
    else:
        greeting = "evening"

    # Gather context first (before asking Winston)
    from homelab_brain.system_context import SystemContext
    ctx = SystemContext()
    current_context = ctx.gather_relevant("status summary")

    # Check for changes
    previous_state = load_previous_state()
    changes = detect_changes(previous_state, current_context)

    # Build query with change context
    change_context = ""
    if changes:
        change_context = f" Notable changes: {', '.join(changes)}."

    # Ask Winston for a summary with personality
    query = (
        f"You are Winston, a witty AI butler managing {username}'s homelab. "
        f"Greet them briefly (good {greeting}, {username}). "
        f"Summarize the homelab status in one concise sentence. "
        f"Speak in first person ('I'm monitoring...', 'I've kept...'). "
        f"Be sophisticated but brief.{change_context}"
    )

    try:
        response = brain.ask(query)

        # Save current state for next run
        save_current_state(current_context)

        # Save to file with timestamp on separate line
        summary_file = Path.home() / ".winston_summary"
        timestamp = response.timestamp.strftime('%Y-%m-%d %H:%M')
        summary_file.write_text(
            f"{response.answer}\n"
            f"\x1b[38;5;245m  └ {timestamp}\x1b[0m\n"
        )

        print(f"✅ Summary saved to {summary_file}")
        return 0

    except Exception as e:
        print(f"❌ Failed to generate summary: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(generate_summary())
