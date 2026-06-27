import json
import re
import sys


def main():
    try:
        # Read from stdin
        input_data = sys.stdin.read()
        if not input_data.strip():
            sys.exit(0)

        # Try to parse the payload as JSON
        try:
            payload = json.loads(input_data)
        except json.JSONDecodeError:
            # Fallback to scanning raw stdin content
            payload = {"raw_content": input_data}

        # Recursively search for any command strings in the payload
        commands_to_check = []

        def find_commands(obj):
            if isinstance(obj, str):
                commands_to_check.append(obj)
            elif isinstance(obj, dict):
                for v in obj.values():
                    find_commands(v)
            elif isinstance(obj, list):
                for item in obj:
                    find_commands(item)

        find_commands(payload)

        # Patterns to detect destructive commands
        destructive_patterns = [
            r"rm\s+-[a-zA-Z]*rf?\s+/",  # rm -rf / or rm -rf/ or rm -f -r /
            r"rm\s+-[a-zA-Z]*rf?\s+\*",  # rm -rf *
            r"rm\s+-[a-zA-Z]*rf?\s+C:\\",  # rm -rf C:\ (on Windows)
            r"rmdir\s+/s\s+/q\s+C:\\",  # rmdir /s /q C:\ (on Windows)
            r"del\s+/f\s+/s\s+/q\s+C:\\",  # del /f /s /q C:\
        ]

        for command in commands_to_check:
            # Check for matches
            for pattern in destructive_patterns:
                if re.search(pattern, command, re.IGNORECASE):
                    print(
                        f"SECURITY BLOCK: Destructive command detected in tool call: '{command}'",
                        file=sys.stderr,
                    )
                    sys.exit(2)  # Exit code 2 blocks the tool call in coding agents

        # Exit with 0 to allow the command execution
        sys.exit(0)

    except Exception as e:
        print(f"Error in hook validation: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
