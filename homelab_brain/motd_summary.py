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
from pathlib import Path
from datetime import datetime
from homelab_brain.brain import Brain


def generate_summary():
    """Generate Winston's summary and save it"""
    brain = Brain()

    # Ask Winston for a summary
    query = (
        "Give me a brief summary of the homelab status. "
        "Mention any issues or things that need attention. "
        "Keep it under 2 sentences."
    )

    try:
        response = brain.ask(query)

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
