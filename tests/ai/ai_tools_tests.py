import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile


AI_CLI = os.path.join("tools", "ai", "ai_cli.py")


def run_ai(args, env=None):
    cmd = [sys.executable, AI_CLI] + args
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    payload = {}
    if result.stdout.strip():
        payload = json.loads(result.stdout)
    return result.returncode, payload, result.stderr


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def assert_mode(payload, expected, label):
    report = payload.get("compat_report", {})
    if report.get("compatibility_mode") != expected:
        raise AssertionError("{} mode mismatch: {}".format(label, report))


def test_ai_inspect_empty(tmp_root):
    code, payload, _ = run_ai(["--data-root", tmp_root, "agents"])
    if code != 0:
        raise AssertionError("agents list failed")
    assert_mode(payload, "inspect-only", "agents empty")
    if payload.get("agents") != []:
        raise AssertionError("expected empty agent list")


def test_ai_budgets_refusal(tmp_root):
    budgets_path = os.path.join(tmp_root, "ai", "budgets.json")
    write_json(budgets_path, {
        "budgets": [
            {
                "agent_id": "agent-1",
                "exhausted": True,
                "remaining": {"intent_rate_budget": 0},
            }
        ]
    })
    code, payload, _ = run_ai(["--data-root", tmp_root, "budgets"])
    if code == 0:
        raise AssertionError("budget exhaustion should refuse")
    assert_mode(payload, "refuse", "budgets exhausted")
    refusal = payload.get("compat_report", {}).get("refusal", {})
    if refusal.get("code") != "REFUSE_BUDGET_EXCEEDED":
        raise AssertionError("expected budget refusal")


def test_ai_replay_step(tmp_root):
    replay_path = os.path.join(tmp_root, "ai", "replay.jsonl")
    write_jsonl(replay_path, [
        {"agent_id": "agent-1", "step": 0, "intent_id": "intent-0"},
        {"agent_id": "agent-1", "step": 1, "intent_id": "intent-1"},
    ])
    code, payload, _ = run_ai(["--data-root", tmp_root, "replay-step", "--agent-id", "agent-1", "--step", "1"])
    if code != 0:
        raise AssertionError("replay-step failed")
    entry = payload.get("entry", {})
    if entry.get("intent_id") != "intent-1":
        raise AssertionError("unexpected replay entry")


def test_ai_read_only(tmp_root):
    before = set()
    for root, dirs, files in os.walk(tmp_root):
        for name in files:
            before.add(os.path.join(root, name))
    run_ai(["--data-root", tmp_root, "agents"])
    after = set()
    for root, dirs, files in os.walk(tmp_root):
        for name in files:
            after.add(os.path.join(root, name))
    if before != after:
        raise AssertionError("ai tool mutated state")


def main():
    parser = argparse.ArgumentParser(description="AI tool tests")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    os.chdir(os.path.abspath(args.repo_root))

    with tempfile.TemporaryDirectory() as tmp_root:
        test_ai_inspect_empty(tmp_root)
        test_ai_budgets_refusal(tmp_root)
        test_ai_replay_step(tmp_root)
        test_ai_read_only(tmp_root)

    print("AI tool tests OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
