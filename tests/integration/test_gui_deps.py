import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Verify tests do not link GUI frameworks directly.")
    parser.add_argument("--report", required=True, help="Path to the GUI dependency report")
    args = parser.parse_args()

    report_path = os.path.abspath(args.report)
    if not os.path.isfile(report_path):
        sys.stderr.write("FAIL: report not found: {}\n".format(report_path))
        return 1

    violations = []
    with open(report_path, "r", encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("violation="):
                payload = line[len("violation="):]
                parts = payload.split("|", 2)
                target = parts[0] if len(parts) > 0 else payload
                link = parts[1] if len(parts) > 1 else ""
                token = parts[2] if len(parts) > 2 else ""
                violations.append((target, link, token))

    if violations:
        for target, link, token in violations:
            sys.stderr.write(
                "FAIL: test target '{}' links forbidden GUI dependency '{}' (matched '{}')\n".format(
                    target, link, token
                )
            )
        return 1

    print("Test GUI dependency check OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
