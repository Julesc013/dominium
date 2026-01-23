import argparse
import os
import subprocess
import sys


def parse_report(path):
    data = {}
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or "=" not in line:
                continue
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip()
    return data


def split_list(value):
    if not value:
        return []
    return [item for item in value.split(";") if item]


def run_cmd(cmd, expect_code=0, expect_nonzero=False, expect_contains=None):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
    )
    output = result.stdout
    if expect_nonzero:
        if result.returncode == 0:
            sys.stderr.write("FAIL: expected non-zero exit for {}\n".format(cmd))
            sys.stderr.write(output)
            return False
    elif expect_code is not None and result.returncode != expect_code:
        sys.stderr.write("FAIL: expected exit {} for {}\n".format(expect_code, cmd))
        sys.stderr.write(output)
        return False
    if expect_contains:
        for token in expect_contains:
            if token not in output:
                sys.stderr.write("FAIL: missing '{}' in output for {}\n".format(token, cmd))
                sys.stderr.write(output)
                return False
    return True


def parse_renderer_caps(output):
    names = set()
    for line in output.splitlines():
        if line.startswith("renderer="):
            head = line.split(" ", 1)[0]
            parts = head.split("=", 1)
            if len(parts) == 2 and parts[1]:
                names.add(parts[1].strip())
    return names


def main():
    parser = argparse.ArgumentParser(description="Validate renderer backend wiring.")
    parser.add_argument("--client", required=True)
    parser.add_argument("--launcher", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    report_path = os.path.abspath(args.report)
    if not os.path.isfile(report_path):
        sys.stderr.write("FAIL: integration report not found: {}\n".format(report_path))
        return 1

    data = parse_report(report_path)
    backend_entries = split_list(data.get("registered_renderer_backends", ""))
    backends = []
    for entry in backend_entries:
        parts = entry.split("|", 1)
        name = parts[0].strip()
        availability = parts[1].strip() if len(parts) > 1 else "unknown"
        if name:
            backends.append((name, availability))

    if not backends:
        sys.stderr.write("FAIL: no registered renderer backends\n")
        return 1

    caps_cmd = [args.launcher, "capabilities"]
    caps_out = subprocess.run(
        caps_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
    ).stdout
    caps_names = parse_renderer_caps(caps_out)

    ok = True
    for name, _availability in backends:
        if name not in caps_names:
            sys.stderr.write("FAIL: renderer '{}' missing from launcher capabilities\n".format(name))
            ok = False

    for name, availability in backends:
        if availability != "unavailable":
            continue
        ok = ok and run_cmd(
            [args.client, "--ui=none", "--renderer=" + name, "--smoke"],
            expect_nonzero=True,
            expect_contains=["unavailable"],
        )

    if ok:
        print("Renderer backend contracts OK.")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
