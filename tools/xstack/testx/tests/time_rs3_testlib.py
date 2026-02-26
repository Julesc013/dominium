"""Shared helpers for RS-3 time constitution TestX cases."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple


def load_fixture(repo_root: str) -> dict:
    fixture_path = os.path.join(
        repo_root,
        "tools",
        "xstack",
        "testdata",
        "session",
        "session_create_input.fixture.json",
    )
    return json.load(open(fixture_path, "r", encoding="utf-8"))


def create_session(
    repo_root: str,
    *,
    save_id: str,
    time_control_policy_id: str,
    physics_profile_id: str = "",
) -> Tuple[dict, Dict[str, object]]:
    from tools.xstack.sessionx.creator import create_session_spec

    fixture = load_fixture(repo_root)
    created = create_session_spec(
        repo_root=repo_root,
        save_id=str(save_id),
        bundle_id=str(fixture.get("bundle_id", "bundle.base.lab")),
        scenario_id=str(fixture.get("scenario_id", "scenario.lab.galaxy_nav")),
        mission_id="",
        experience_id=str(fixture.get("experience_id", "profile.lab.developer")),
        law_profile_id=str(fixture.get("law_profile_id", "law.lab.unrestricted")),
        parameter_bundle_id=str(fixture.get("parameter_bundle_id", "params.lab.placeholder")),
        budget_policy_id=str(fixture.get("budget_policy_id", "policy.budget.default_lab")),
        fidelity_policy_id=str(fixture.get("fidelity_policy_id", "policy.fidelity.default_lab")),
        rng_seed_string=str(fixture.get("rng_seed_string", "seed.testx.session.fixture")),
        rng_roots=[],
        universe_identity_path="",
        universe_seed_string=str(fixture.get("universe_seed_string", "seed.testx.universe.fixture")),
        universe_id="",
        entitlements=list(fixture.get("entitlements") or []),
        epistemic_scope_id=str(fixture.get("epistemic_scope_id", "epistemic.lab.placeholder")),
        visibility_level=str(fixture.get("visibility_level", "placeholder")),
        privilege_level=str(fixture.get("privilege_level", "operator")),
        physics_profile_id=str(physics_profile_id).strip() or "physics.null",
        time_control_policy_id=str(time_control_policy_id),
        compile_outputs=True,
        saves_root_rel="saves",
    )
    return fixture, created


def write_script(repo_root: str, save_id: str, script_id: str, intents: List[dict]) -> str:
    script_payload = {
        "schema_version": "1.0.0",
        "script_id": str(script_id),
        "intents": list(intents or []),
    }
    script_rel = os.path.join("saves", str(save_id), "script.{}.json".format(str(script_id).replace(".", "_")))
    script_abs = os.path.join(repo_root, script_rel.replace("/", os.sep))
    parent = os.path.dirname(script_abs)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(script_abs, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(script_payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return script_abs


def run_script(
    repo_root: str,
    *,
    created: dict,
    fixture: dict,
    script_abs: str,
    write_state: bool,
) -> dict:
    from tools.xstack.sessionx.script_runner import run_intent_script

    session_spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    return run_intent_script(
        repo_root=repo_root,
        session_spec_path=session_spec_abs,
        script_path=script_abs,
        bundle_id=str(fixture.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
        workers=1,
        write_state=bool(write_state),
    )


def run_script_with_session_spec(
    repo_root: str,
    *,
    session_spec_path: str,
    bundle_id: str,
    script_abs: str,
    write_state: bool,
) -> dict:
    from tools.xstack.sessionx.script_runner import run_intent_script

    session_spec_abs = os.path.join(repo_root, str(session_spec_path).replace("/", os.sep))
    return run_intent_script(
        repo_root=repo_root,
        session_spec_path=session_spec_abs,
        script_path=script_abs,
        bundle_id=str(bundle_id),
        compile_if_missing=False,
        workers=1,
        write_state=bool(write_state),
    )


def load_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, str(rel_path).replace("/", os.sep))
    return json.load(open(abs_path, "r", encoding="utf-8"))


def load_state_after_run(repo_root: str, created: dict) -> dict:
    state_abs = os.path.join(repo_root, str(created.get("universe_state_path", "")).replace("/", os.sep))
    return json.load(open(state_abs, "r", encoding="utf-8"))


def checkpoint_id_from_run_result(repo_root: str, run_result: dict) -> str:
    checkpoint_paths = list(run_result.get("checkpoint_artifact_paths") or [])
    if not checkpoint_paths:
        return ""
    first = str(sorted(checkpoint_paths)[0])
    payload = load_json(repo_root, first)
    return str(payload.get("checkpoint_id", "")).strip()


def checkpoint_payloads_from_run_result(repo_root: str, run_result: dict) -> List[dict]:
    rows: List[dict] = []
    checkpoint_paths = list(run_result.get("checkpoint_artifact_paths") or [])
    for rel_path in sorted(str(path) for path in checkpoint_paths):
        payload = load_json(repo_root, rel_path)
        rows.append(dict(payload))
    return rows


def camera_move_intents(count: int, *, prefix: str = "intent") -> List[dict]:
    rows: List[dict] = []
    for idx in range(1, int(count) + 1):
        rows.append(
            {
                "intent_id": "{}.{:03d}".format(str(prefix), int(idx)),
                "process_id": "process.camera_move",
                "inputs": {
                    "delta_local_mm": {
                        "x": int(100 + idx),
                        "y": int(idx % 3),
                        "z": int(-(idx % 5)),
                    },
                    "dt_ticks": 1,
                },
            }
        )
    return rows


def default_variable_dt_policy_context() -> dict:
    return {
        "time_control_policy_id": "time.policy.default_realistic",
        "time_control_policy": {
            "time_control_policy_id": "time.policy.default_realistic",
            "allow_variable_dt": True,
            "allow_pause": True,
            "allow_rate_change": True,
            "allowed_rate_range": {"min": 250, "max": 4000},
            "dt_quantization_rule_id": "dt.rule.standard",
        },
        "dt_quantization_rule": {
            "dt_rule_id": "dt.rule.standard",
            "allowed_dt_values": [250, 500, 1000, 2000, 4000],
            "default_dt": 1000,
            "deterministic_rounding_rule": "round.nearest.lower_tie",
        },
    }
