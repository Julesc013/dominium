import argparse
import json
import os
import subprocess
import sys
import tempfile


REPOX_SCRIPT = os.path.join("scripts", "repox", "repox_update_feeds.py")
CHANNELS = ["stable", "beta", "nightly", "pinned"]
DETERMINISTIC_TS = "2000-01-01T00:00:00Z"


def write_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def read_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def run_cmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise AssertionError("command failed: {}\n{}".format(" ".join(cmd), result.stderr))
    return result


def assert_feed(feed: dict, channel: str, expected_entries: int, expected_rollbacks: int) -> None:
    if feed.get("schema_version") != 1:
        raise AssertionError("schema_version mismatch for {}".format(channel))
    if feed.get("channel") != channel:
        raise AssertionError("channel mismatch for {}".format(channel))
    if feed.get("generated_at") != DETERMINISTIC_TS:
        raise AssertionError("generated_at mismatch for {}".format(channel))
    entries = feed.get("entries")
    rollbacks = feed.get("rollbacks")
    if not isinstance(entries, list) or len(entries) != expected_entries:
        raise AssertionError("entries list mismatch for {}".format(channel))
    if not isinstance(rollbacks, list) or len(rollbacks) != expected_rollbacks:
        raise AssertionError("rollbacks list mismatch for {}".format(channel))


def main() -> int:
    parser = argparse.ArgumentParser(description="RepoX update feed tests")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    os.chdir(repo_root)

    with tempfile.TemporaryDirectory() as tmp_root:
        updates_root = os.path.join(tmp_root, "updates")
        os.makedirs(updates_root, exist_ok=True)
        write_json(os.path.join(updates_root, "stable.json"), {
            "entries": [{"id": "entry-1"}],
            "rollbacks": ["rollback-1"],
        })

        run_cmd([
            sys.executable,
            REPOX_SCRIPT,
            "--repo-root", tmp_root,
            "--deterministic",
        ])

        for channel in CHANNELS:
            feed_path = os.path.join(updates_root, "{}.json".format(channel))
            if not os.path.isfile(feed_path):
                raise AssertionError("missing feed for {}".format(channel))
            feed = read_json(feed_path)
            if channel == "stable":
                assert_feed(feed, channel, 1, 1)
            else:
                assert_feed(feed, channel, 0, 0)

    print("RepoX update feed tests OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
