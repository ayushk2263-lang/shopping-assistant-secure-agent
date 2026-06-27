import os
import re
import sys


def main():
    pattern = re.compile(r"AIz" + r"aSy[A-Za-z0-9_\-]*")

    # Files are passed as arguments by pre-commit
    files_to_scan = [
        arg for arg in sys.argv[1:] if arg.endswith(".py") and os.path.exists(arg)
    ]

    # Fallback to recursively scanning python files in the current folder if none passed
    if not files_to_scan:
        for root, _, files in os.walk("."):
            for file in files:
                if file.endswith(".py") and ".venv" not in root:
                    files_to_scan.append(os.path.join(root, file))

    findings = 0
    for filepath in files_to_scan:
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            # Scan file contents
            for match in pattern.finditer(content):
                # Calculate line number
                line_no = content[: match.start()].count("\n") + 1
                matched_text = match.group()

                print(
                    f"[ERROR] {filepath}:{line_no} - detect-gcp-api-key",
                    file=sys.stderr,
                )
                print(
                    "  Security Warning: Detected a hardcoded Google API key prefix. Never store API keys or secrets in source code.",
                    file=sys.stderr,
                )
                print(f"  Match: {matched_text}", file=sys.stderr)
                findings += 1
        except Exception as e:
            print(f"Error reading {filepath}: {e}", file=sys.stderr)

    if findings > 0:
        print(
            f"\nSemgrep Local Scan: {findings} vulnerability findings. Commit aborted.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("Semgrep Local Scan: No findings.")
    sys.exit(0)


if __name__ == "__main__":
    main()
