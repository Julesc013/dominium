#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys


STRICT_CMAKE_ARGS = (
    "-G",
    "Ninja",
    "-DCMAKE_BUILD_TYPE=Debug",
    "-DDOM_DISALLOW_DOWNLOADS=ON",
    "-DFETCHCONTENT_FULLY_DISCONNECTED=ON",
    "-DFETCHCONTENT_UPDATES_DISCONNECTED=ON",
    "-DDOM_PLATFORM=posix_headless",
    "-DDOM_BACKEND_SOFT=OFF",
    "-DDOM_BACKEND_NULL=ON",
    "-DDOM_ENABLE_NET=ON",
    "-DDOM_BUILD_TESTS=ON",
    "-DDOM_BUILD_TOOLS=ON",
)


def github_escape(text):
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def emit_failure_annotation(label, failed_command, lines):
    tail = [line.rstrip("\n") for line in lines if line.strip()]
    if len(tail) > 24:
        tail = tail[-24:]
    message = "Command failed: {}\n\n{}".format(" ".join(failed_command), "\n".join(tail))
    sys.stdout.write("::error title=Strict build {}::{}\n".format(label, github_escape(message)))
    step_summary = os.environ.get("GITHUB_STEP_SUMMARY", "")
    if step_summary:
        with open(step_summary, "a", encoding="utf-8") as handle:
            handle.write("## Strict build {} failure tail\n\n".format(label))
            handle.write("```text\n")
            handle.write(message)
            if not message.endswith("\n"):
                handle.write("\n")
            handle.write("```\n")


def run_and_capture(command, cwd):
    proc = subprocess.Popen(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    lines = []
    assert proc.stdout is not None
    for line in proc.stdout:
        sys.stdout.write(line)
        lines.append(line)
    proc.wait()
    return proc.returncode, lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--build-dir", required=True)
    parser.add_argument("--label", required=True)
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    build_dir = args.build_dir
    label = args.label

    configure_cmd = ["cmake", "-S", ".", "-B", build_dir] + list(STRICT_CMAKE_ARGS)
    build_cmd = ["cmake", "--build", build_dir, "--config", "Debug"]

    for command in (configure_cmd, build_cmd):
        rc, lines = run_and_capture(command, repo_root)
        if rc != 0:
            emit_failure_annotation(label, command, lines)
            return rc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
