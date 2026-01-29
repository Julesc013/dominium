import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple


DEFAULT_BUDGET_FILE = os.path.join("ai", "budgets.json")
DEFAULT_AGENTS_FILE = os.path.join("ai", "agents.json")
DEFAULT_INTENT_FILE = os.path.join("ai", "intents.jsonl")
DEFAULT_REPLAY_FILE = os.path.join("ai", "replay.jsonl")
DEFAULT_CAPABILITY_BASELINE = "BASELINE_MAINLINE_CORE"
NULL_UUID = "00000000-0000-0000-0000-000000000000"


def now_timestamp(deterministic: bool) -> str:
    if deterministic or os.environ.get("OPS_DETERMINISTIC") == "1":
        return "2000-01-01T00:00:00Z"
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: str) -> List[dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def sorted_unique(values: Optional[List[str]]) -> List[str]:
    if not values:
        return []
    return sorted({value for value in values if value})


def refusal_payload(code_id: int, code: str, message: str, details: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    return {
        "code_id": code_id,
        "code": code,
        "message": message,
        "details": details or {},
        "explanation_classification": "PUBLIC",
    }


def build_compat_report(context: str,
                        install_id: Optional[str],
                        instance_id: Optional[str],
                        runtime_id: Optional[str],
                        capability_baseline: Optional[str],
                        required_capabilities: Optional[List[str]],
                        provided_capabilities: Optional[List[str]],
                        missing_capabilities: Optional[List[str]],
                        compatibility_mode: str,
                        refusal_codes: Optional[List[str]],
                        mitigation_hints: Optional[List[str]],
                        deterministic: bool,
                        extensions: Optional[Dict[str, object]] = None,
                        refusal: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    required = sorted_unique(required_capabilities)
    provided = sorted_unique(provided_capabilities)
    missing = sorted_unique(missing_capabilities)
    if missing_capabilities is None:
        missing = sorted(set(required) - set(provided))
    payload = {
        "context": context,
        "install_id": install_id or NULL_UUID,
        "instance_id": instance_id or NULL_UUID,
        "runtime_id": runtime_id or NULL_UUID,
        "capability_baseline": capability_baseline or DEFAULT_CAPABILITY_BASELINE,
        "required_capabilities": required,
        "provided_capabilities": provided,
        "missing_capabilities": missing,
        "compatibility_mode": compatibility_mode,
        "refusal_codes": sorted_unique(refusal_codes),
        "mitigation_hints": sorted_unique(mitigation_hints),
        "timestamp": now_timestamp(deterministic),
        "extensions": extensions or {},
    }
    if refusal:
        payload["refusal"] = refusal
    return payload


def read_agents(path: str) -> List[dict]:
    if not os.path.isfile(path):
        return []
    payload = load_json(path)
    return payload.get("agents", [])


def read_budgets(path: str) -> List[dict]:
    if not os.path.isfile(path):
        return []
    payload = load_json(path)
    return payload.get("budgets", [])


def budgets_exhausted(budgets: List[dict]) -> Optional[dict]:
    for entry in budgets:
        if entry.get("exhausted") is True:
            return entry
        remaining = entry.get("remaining")
        if isinstance(remaining, dict):
            for key, value in remaining.items():
                if isinstance(value, (int, float)) and value <= 0:
                    return entry
    return None


def ai_agents(args: argparse.Namespace) -> Tuple[int, Dict[str, object]]:
    agents = read_agents(os.path.join(args.data_root, DEFAULT_AGENTS_FILE))
    report = build_compat_report(
        context="load",
        install_id=args.install_id,
        instance_id=args.instance_id,
        runtime_id=args.runtime_id,
        capability_baseline=args.capability_baseline,
        required_capabilities=[],
        provided_capabilities=[],
        missing_capabilities=[],
        compatibility_mode="inspect-only",
        refusal_codes=[],
        mitigation_hints=[],
        deterministic=args.deterministic,
        extensions={"agent_count": len(agents)},
        refusal=None,
    )
    return 0, {"result": "ok", "compat_report": report, "agents": agents}


def ai_budgets(args: argparse.Namespace) -> Tuple[int, Dict[str, object]]:
    budgets = read_budgets(os.path.join(args.data_root, DEFAULT_BUDGET_FILE))
    if args.agent_id:
        budgets = [b for b in budgets if b.get("agent_id") == args.agent_id]
    exhausted = budgets_exhausted(budgets)
    refusal = None
    refusal_codes: List[str] = []
    mode = "inspect-only"
    mitigation: List[str] = []
    if exhausted:
        refusal = refusal_payload(7, "REFUSE_BUDGET_EXCEEDED",
                                  "ai budget exhausted",
                                  {"agent_id": exhausted.get("agent_id")})
        refusal_codes = [refusal.get("code")]
        mitigation = ["adjust ai budget meta-law configuration"]
        mode = "refuse"
    report = build_compat_report(
        context="load",
        install_id=args.install_id,
        instance_id=args.instance_id,
        runtime_id=args.runtime_id,
        capability_baseline=args.capability_baseline,
        required_capabilities=[],
        provided_capabilities=[],
        missing_capabilities=[],
        compatibility_mode=mode,
        refusal_codes=refusal_codes,
        mitigation_hints=mitigation,
        deterministic=args.deterministic,
        extensions={"budgets": budgets},
        refusal=refusal,
    )
    return (3 if mode == "refuse" else 0), {"result": "refused" if mode == "refuse" else "ok",
                                            "compat_report": report,
                                            "budgets": budgets}


def ai_intents(args: argparse.Namespace) -> Tuple[int, Dict[str, object]]:
    intents_path = os.path.join(args.data_root, DEFAULT_INTENT_FILE)
    intents = []
    if os.path.isfile(intents_path):
        intents = load_jsonl(intents_path)
    if args.agent_id:
        intents = [row for row in intents if row.get("agent_id") == args.agent_id]
    if args.limit and len(intents) > args.limit:
        intents = intents[-args.limit:]
    report = build_compat_report(
        context="load",
        install_id=args.install_id,
        instance_id=args.instance_id,
        runtime_id=args.runtime_id,
        capability_baseline=args.capability_baseline,
        required_capabilities=[],
        provided_capabilities=[],
        missing_capabilities=[],
        compatibility_mode="inspect-only",
        refusal_codes=[],
        mitigation_hints=[],
        deterministic=args.deterministic,
        extensions={"intent_count": len(intents)},
        refusal=None,
    )
    return 0, {"result": "ok", "compat_report": report, "intents": intents}


def ai_replay_step(args: argparse.Namespace) -> Tuple[int, Dict[str, object]]:
    replay_path = os.path.join(args.data_root, DEFAULT_REPLAY_FILE)
    entries = []
    if os.path.isfile(replay_path):
        entries = load_jsonl(replay_path)
    if args.agent_id:
        entries = [row for row in entries if row.get("agent_id") == args.agent_id]
    step = args.step
    selected = entries[step] if step is not None and step < len(entries) else None
    report = build_compat_report(
        context="load",
        install_id=args.install_id,
        instance_id=args.instance_id,
        runtime_id=args.runtime_id,
        capability_baseline=args.capability_baseline,
        required_capabilities=[],
        provided_capabilities=[],
        missing_capabilities=[],
        compatibility_mode="inspect-only",
        refusal_codes=[],
        mitigation_hints=[],
        deterministic=args.deterministic,
        extensions={"replay_length": len(entries)},
        refusal=None,
    )
    return 0, {"result": "ok", "compat_report": report, "entry": selected}


def main() -> int:
    parser = argparse.ArgumentParser(description="AI inspection CLI (read-only)")
    parser.add_argument("--data-root", default=".")
    parser.add_argument("--install-id", default=None)
    parser.add_argument("--instance-id", default=None)
    parser.add_argument("--runtime-id", default=None)
    parser.add_argument("--capability-baseline", default=DEFAULT_CAPABILITY_BASELINE)
    parser.add_argument("--deterministic", action="store_true")
    sub = parser.add_subparsers(dest="cmd")

    agents = sub.add_parser("agents")
    agents.add_argument("--agent-id", default=None)

    budgets = sub.add_parser("budgets")
    budgets.add_argument("--agent-id", default=None)

    intents = sub.add_parser("intents")
    intents.add_argument("--agent-id", default=None)
    intents.add_argument("--limit", type=int, default=None)

    replay = sub.add_parser("replay-step")
    replay.add_argument("--agent-id", default=None)
    replay.add_argument("--step", type=int, default=0)

    args = parser.parse_args()

    if args.cmd == "agents":
        code, output = ai_agents(args)
        print(json.dumps(output, indent=2))
        return code
    if args.cmd == "budgets":
        code, output = ai_budgets(args)
        print(json.dumps(output, indent=2))
        return code
    if args.cmd == "intents":
        code, output = ai_intents(args)
        print(json.dumps(output, indent=2))
        return code
    if args.cmd == "replay-step":
        code, output = ai_replay_step(args)
        print(json.dumps(output, indent=2))
        return code

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
