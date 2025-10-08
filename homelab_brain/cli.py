#!/usr/bin/env python3
"""
CLI for Winston - Your homelab AI assistant

Usage:
    lab ask "How much memory is free?"
    lab status
"""
import sys
from homelab_brain.brain import Brain


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  lab ask <question>    - Ask Winston a question")
        print("  lab status            - Quick system status")
        sys.exit(1)

    command = sys.argv[1]

    if command == "ask":
        if len(sys.argv) < 3:
            print("Error: Please provide a question")
            print('Example: lab ask "How much memory is available?"')
            sys.exit(1)

        question = " ".join(sys.argv[2:])
        brain = Brain()

        response = brain.ask(question)
        print(f"\n{response.answer}\n")

    elif command == "status":
        brain = Brain()
        response = brain.ask("Give me a quick status summary of the system")

        print(f"\n{response.answer}\n")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
