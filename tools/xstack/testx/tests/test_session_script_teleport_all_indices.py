"""STRICT test: teleport-to-all object/site IDs replays deterministically."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.session.teleport_all_indices_determinism"
TEST_TAGS = ["strict", "session", "registry"]


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def _load_fixture(repo_root: str, rel_path: str):
    return _load_json(os.path.join(repo_root, rel_path.replace("/", os.sep)))


def _build_script_payload(object_ids, site_ids):
    intents = []
    index = 1
    for object_id in sorted(set(str(item).strip() for item in object_ids if str(item).strip())):
        intents.append(
            {
                "intent_id": "intent.teleport.object.{:04d}".format(index),
                "process_id": "process.camera_teleport",
                "inputs": {
                    "target_object_id": object_id
                },
            }
        )
        index += 1
    for site_id in sorted(set(str(item).strip() for item in site_ids if str(item).strip())):
        intents.append(
            {
                "intent_id": "intent.teleport.site.{:04d}".format(index),
                "process_id": "process.camera_teleport",
                "inputs": {
                    "target_site_id": site_id
                },
            }
        )
        index += 1
    return {
        "schema_version": "1.0.0",
        "script_id": "script.testx.teleport_all_indices.v1",
        "intents": intents,
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.creator import create_session_spec
    from tools.xstack.sessionx.script_runner import run_intent_script

    session_fixture = _load_fixture(repo_root, "tools/xstack/testdata/session/session_create_input.fixture.json")
    save_id = str(session_fixture.get("save_id", "save.testx.session.fixture")) + ".teleport_all"
    created = create_session_spec(
        repo_root=repo_root,
        save_id=save_id,
        bundle_id=str(session_fixture.get("bundle_id", "bundle.base.lab")),
        scenario_id=str(session_fixture.get("scenario_id", "scenario.lab.galaxy_nav")),
        mission_id="",
        experience_id=str(session_fixture.get("experience_id", "profile.lab.developer")),
        law_profile_id=str(session_fixture.get("law_profile_id", "law.lab.unrestricted")),
        parameter_bundle_id=str(session_fixture.get("parameter_bundle_id", "params.lab.placeholder")),
        budget_policy_id=str(session_fixture.get("budget_policy_id", "policy.budget.default_lab")),
        fidelity_policy_id=str(session_fixture.get("fidelity_policy_id", "policy.fidelity.default_lab")),
        rng_seed_string=str(session_fixture.get("rng_seed_string", "seed.testx.session.fixture")),
        rng_roots=[],
        universe_identity_path="",
        universe_seed_string=str(session_fixture.get("universe_seed_string", "seed.testx.universe.fixture")),
        universe_id="",
        entitlements=list(session_fixture.get("entitlements") or []),
        epistemic_scope_id=str(session_fixture.get("epistemic_scope_id", "epistemic.lab.placeholder")),
        visibility_level=str(session_fixture.get("visibility_level", "placeholder")),
        privilege_level=str(session_fixture.get("privilege_level", "operator")),
        compile_outputs=True,
        saves_root_rel="saves",
    )
    if created.get("result") != "complete":
        return {"status": "fail", "message": "session create failed before teleport-all determinism test"}

    astronomy_payload = _load_json(os.path.join(repo_root, "build", "registries", "astronomy.catalog.index.json"))
    site_payload = _load_json(os.path.join(repo_root, "build", "registries", "site.registry.index.json"))
    object_ids = [row.get("object_id", "") for row in (astronomy_payload.get("entries") or []) if isinstance(row, dict)]
    site_ids = [row.get("site_id", "") for row in (site_payload.get("sites") or []) if isinstance(row, dict)]
    if not object_ids:
        return {"status": "fail", "message": "astronomy index has no object ids for teleport-all test"}
    if not site_ids:
        return {"status": "fail", "message": "site index has no site ids for teleport-all test"}

    script_payload = _build_script_payload(object_ids=object_ids, site_ids=site_ids)
    script_path = os.path.join(repo_root, "saves", save_id, "script.teleport_all_indices.fixture.json")
    os.makedirs(os.path.dirname(script_path), exist_ok=True)
    with open(script_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(script_payload, handle, indent=2, sort_keys=True)
        handle.write("\n")

    spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    first = run_intent_script(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        script_path=script_path,
        bundle_id=str(session_fixture.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
        workers=1,
        write_state=False,
    )
    second = run_intent_script(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        script_path=script_path,
        bundle_id=str(session_fixture.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
        workers=1,
        write_state=False,
    )
    if first.get("result") != "complete" or second.get("result") != "complete":
        return {"status": "fail", "message": "teleport-all script execution failed"}

    for key in ("final_state_hash", "deterministic_fields_hash", "pack_lock_hash"):
        if str(first.get(key, "")) != str(second.get(key, "")):
            return {"status": "fail", "message": "determinism mismatch for '{}'".format(key)}
    if list(first.get("state_hash_anchors") or []) != list(second.get("state_hash_anchors") or []):
        return {"status": "fail", "message": "state hash anchors mismatch for teleport-all replay"}
    if len(list(first.get("state_hash_anchors") or [])) != len(list(script_payload.get("intents") or [])):
        return {"status": "fail", "message": "missing state hash anchors for teleport-all intents"}

    return {"status": "pass", "message": "teleport-all object/site deterministic replay passed"}
