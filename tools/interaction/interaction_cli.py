#!/usr/bin/env python3
"""CLI command surface for deterministic interaction affordances and dispatch."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.sessionx.interaction import run_interaction_command


def _repo_root(token: str) -> str:
    value = str(token or "").strip()
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def _read_json(path: str) -> tuple[dict, str]:
    target = os.path.normpath(os.path.abspath(str(path or "").strip()))
    if not os.path.isfile(target):
        return {}, "missing file: {}".format(target.replace("\\", "/"))
    try:
        with open(target, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}, "invalid json: {}".format(target.replace("\\", "/"))
    if not isinstance(payload, dict):
        return {}, "json root must be object: {}".format(target.replace("\\", "/"))
    return payload, ""


def _parse_params(params_inline: str, params_file: str) -> tuple[dict, str]:
    if str(params_file or "").strip():
        payload, err = _read_json(params_file)
        if err:
            return {}, err
        return payload, ""
    token = str(params_inline or "").strip()
    if not token:
        return {}, ""
    try:
        payload = json.loads(token)
    except ValueError:
        return {}, "invalid --params-inline JSON payload"
    if not isinstance(payload, dict):
        return {}, "--params-inline payload must be a JSON object"
    return payload, ""


def _parse_policy_context(policy_context_file: str) -> tuple[dict, str]:
    token = str(policy_context_file or "").strip()
    if not token:
        return {}, ""
    payload, err = _read_json(token)
    if err:
        return {}, err
    return payload, ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic interaction command surface.")
    parser.add_argument(
        "command",
        choices=("interact.select_target", "interact.list_affordances", "interact.preview", "interact.execute"),
    )
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--perceived", required=True, help="Path to PerceivedModel JSON artifact.")
    parser.add_argument("--law", required=True, help="Path to selected law profile JSON.")
    parser.add_argument("--authority", required=True, help="Path to authority context JSON.")
    parser.add_argument(
        "--interaction-registry",
        required=True,
        help="Path to interaction action registry payload (compiled or source row object).",
    )
    parser.add_argument("--target-id", default="")
    parser.add_argument("--affordance-id", default="")
    parser.add_argument("--params-inline", default="")
    parser.add_argument("--params-file", default="")
    parser.add_argument("--state", default="", help="Path to universe_state JSON (required for interact.execute).")
    parser.add_argument("--peer-id", default="")
    parser.add_argument("--sequence", type=int, default=0)
    parser.add_argument("--submission-tick", type=int, default=0)
    parser.add_argument("--policy-context-file", default="")
    parser.add_argument("--policy-id", default="")
    parser.add_argument("--server-profile-id", default="")
    parser.add_argument("--active-shard-id", default="shard.0")
    parser.add_argument("--source-shard-id", default="shard.0")
    parser.add_argument("--target-shard-id", default="shard.0")
    parser.add_argument("--interaction-max-per-tick", type=int, default=24)
    parser.add_argument("--include-disabled", action="store_true")
    args = parser.parse_args()

    repo_root = _repo_root(args.repo_root)
    perceived_model, perceived_error = _read_json(args.perceived)
    if perceived_error:
        print(json.dumps({"result": "refused", "message": perceived_error}, indent=2, sort_keys=True))
        return 1
    law_profile, law_error = _read_json(args.law)
    if law_error:
        print(json.dumps({"result": "refused", "message": law_error}, indent=2, sort_keys=True))
        return 1
    authority_context, authority_error = _read_json(args.authority)
    if authority_error:
        print(json.dumps({"result": "refused", "message": authority_error}, indent=2, sort_keys=True))
        return 1
    action_registry, action_error = _read_json(args.interaction_registry)
    if action_error:
        print(json.dumps({"result": "refused", "message": action_error}, indent=2, sort_keys=True))
        return 1

    params, params_error = _parse_params(args.params_inline, args.params_file)
    if params_error:
        print(json.dumps({"result": "refused", "message": params_error}, indent=2, sort_keys=True))
        return 1

    state_payload = {}
    if str(args.state or "").strip():
        state_payload, state_error = _read_json(args.state)
        if state_error:
            print(json.dumps({"result": "refused", "message": state_error}, indent=2, sort_keys=True))
            return 1
    if str(args.command) == "interact.execute" and not state_payload:
        print(
            json.dumps(
                {
                    "result": "refused",
                    "message": "interact.execute requires --state universe_state payload",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1

    file_policy_context, file_policy_error = _parse_policy_context(args.policy_context_file)
    if file_policy_error:
        print(json.dumps({"result": "refused", "message": file_policy_error}, indent=2, sort_keys=True))
        return 1
    policy_context = dict(file_policy_context)
    if str(args.policy_id or "").strip():
        policy_context["net_policy_id"] = str(args.policy_id).strip()
    if str(args.server_profile_id or "").strip():
        policy_context["server_profile_id"] = str(args.server_profile_id).strip()
    policy_context["active_shard_id"] = str(args.active_shard_id or "shard.0").strip() or "shard.0"
    policy_context["interaction_max_per_tick"] = int(max(1, int(args.interaction_max_per_tick)))

    result = run_interaction_command(
        command=str(args.command),
        perceived_model=perceived_model,
        law_profile=law_profile,
        authority_context=authority_context,
        interaction_action_registry=action_registry,
        target_semantic_id=str(args.target_id or ""),
        affordance_id=str(args.affordance_id or ""),
        parameters=params,
        state=state_payload,
        navigation_indices={},
        policy_context=policy_context,
        peer_id=str(args.peer_id or ""),
        deterministic_sequence_number=int(args.sequence),
        submission_tick=int(args.submission_tick),
        source_shard_id=str(args.source_shard_id or "shard.0"),
        target_shard_id=str(args.target_shard_id or "shard.0"),
        include_disabled=bool(args.include_disabled),
        repo_root=repo_root,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")) == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
