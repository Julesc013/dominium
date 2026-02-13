import argparse
import json
import os
import sys


LAW_REL = os.path.join("data", "registries", "law_profiles.json")
EXP_REL = os.path.join("data", "registries", "experience_profiles.json")
PARAM_REL = os.path.join("data", "registries", "parameter_bundles.json")
BUNDLE_REL = os.path.join("data", "registries", "bundle_profiles.json")
PIPELINE_REL = os.path.join("client", "core", "session_pipeline.c")
BRIDGE_REL = os.path.join("client", "core", "client_command_bridge.c")
REGISTRY_REL = os.path.join("client", "core", "client_commands_registry.c")
REFUSAL_REL = os.path.join("client", "core", "session_refusal_codes.h")


def _load_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def _load_core_payloads(repo_root: str):
    payloads = {}
    for rel in (LAW_REL, EXP_REL, PARAM_REL, BUNDLE_REL):
        path = os.path.join(repo_root, rel)
        if not os.path.isfile(path):
            return None, "missing {}".format(rel.replace("\\", "/"))
        payload = _load_json(path)
        if payload is None:
            return None, "invalid json {}".format(rel.replace("\\", "/"))
        payloads[rel] = payload
    return payloads, ""


def _case_profile_switch_requires_restart(repo_root: str):
    text = _read_text(os.path.join(repo_root, PIPELINE_REL))
    required = (
        "client.experience.select",
        "CLIENT_SESSION_STAGE_SESSION_RUNNING",
        "CLIENT_SESSION_REFUSE_INVALID_TRANSITION",
    )
    for marker in required:
        if marker not in text:
            return False, "profile switch guard missing marker {} in {}".format(marker, PIPELINE_REL.replace("\\", "/"))
    return True, "profile switch restart guard present"


def _case_remove_optional_bundle_core_boots(repo_root: str):
    payloads, error = _load_core_payloads(repo_root)
    if payloads is None:
        return False, error
    bundles = ((payloads[BUNDLE_REL].get("record") or {}).get("bundles") or [])
    by_id = {}
    for row in bundles:
        if isinstance(row, dict):
            bundle_id = str(row.get("bundle_id", "")).strip()
            if bundle_id:
                by_id[bundle_id] = row
    core = by_id.get("bundle.core.runtime")
    if not isinstance(core, dict):
        return False, "missing bundle.core.runtime"
    if ((core.get("extensions") or {}).get("optional")) is not False:
        return False, "bundle.core.runtime must be non-optional"
    for bundle_id, row in sorted(by_id.items()):
        if bundle_id in {"bundle.core.runtime", "bundle.default_core"}:
            continue
        if ((row.get("extensions") or {}).get("optional")) is not True:
            return False, "{} must stay optional".format(bundle_id)
    return True, "bundle optionality contract preserved"


def _case_survival_to_creative_transition(repo_root: str):
    payloads, error = _load_core_payloads(repo_root)
    if payloads is None:
        return False, error
    experiences = ((payloads[EXP_REL].get("record") or {}).get("profiles") or [])
    by_id = {}
    for row in experiences:
        if isinstance(row, dict):
            exp_id = str(row.get("experience_id", "")).strip()
            if exp_id:
                by_id[exp_id] = row
    survival = by_id.get("exp.survival")
    creative = by_id.get("exp.creative")
    if not isinstance(survival, dict) or not isinstance(creative, dict):
        return False, "missing exp.survival or exp.creative"
    if str(survival.get("law_profile_id", "")).strip() == str(creative.get("law_profile_id", "")).strip():
        return False, "survival and creative must not share the same law profile"
    if str(survival.get("default_parameter_bundle_id", "")).strip() == str(creative.get("default_parameter_bundle_id", "")).strip():
        return False, "survival and creative must not share default parameter bundle"

    bridge = _read_text(os.path.join(repo_root, BRIDGE_REL))
    for marker in (
        "{ \"exp.survival\", \"law.survival.softcore\", 1, 0, 0, 0, 0, 0 }",
        "{ \"exp.creative\", \"law.creative.full\", 1, 1, 1, 1, 0, 1 }",
        "client.session.create_from_selection",
    ):
        if marker not in bridge:
            return False, "missing marker {} in {}".format(marker, BRIDGE_REL.replace("\\", "/"))
    return True, "survival/creative transition contracts present"


def _case_survival_hardcore_delta_only(repo_root: str):
    payloads, error = _load_core_payloads(repo_root)
    if payloads is None:
        return False, error

    law_rows = ((payloads[LAW_REL].get("record") or {}).get("profiles") or [])
    law_by_id = {}
    for row in law_rows:
        if isinstance(row, dict):
            law_id = str(row.get("law_profile_id", "")).strip()
            if law_id:
                law_by_id[law_id] = row

    soft = law_by_id.get("law.survival.softcore")
    hard = law_by_id.get("law.survival.hardcore")
    if not isinstance(soft, dict) or not isinstance(hard, dict):
        return False, "missing law.survival.softcore or law.survival.hardcore"

    soft_allowed = [str(v).strip() for v in (soft.get("allowed_intent_families") or [])]
    hard_allowed = [str(v).strip() for v in (hard.get("allowed_intent_families") or [])]
    if soft_allowed != hard_allowed:
        return False, "hardcore should keep survival allowed intents and apply deltas via forbids/revokes"

    hard_forbidden = [str(v).strip() for v in (hard.get("forbidden_intent_families") or [])]
    for intent in ("intent.revive", "intent.rollback"):
        if intent not in hard_forbidden:
            return False, "hardcore missing forbidden intent {}".format(intent)

    bundle_rows = ((payloads[PARAM_REL].get("record") or {}).get("bundles") or [])
    bundle_by_id = {}
    for row in bundle_rows:
        if isinstance(row, dict):
            bundle_id = str(row.get("parameter_bundle_id", "")).strip()
            if bundle_id:
                bundle_by_id[bundle_id] = row

    default_bundle = (bundle_by_id.get("survival.params.default") or {}).get("parameters") or {}
    harsh_bundle = (bundle_by_id.get("survival.params.harsh") or {}).get("parameters") or {}
    if not isinstance(default_bundle, dict) or not isinstance(harsh_bundle, dict):
        return False, "survival parameter bundles missing"
    if sorted(default_bundle.keys()) != sorted(harsh_bundle.keys()):
        return False, "survival default and harsh bundles must share parameter keys"
    deltas = [key for key in sorted(default_bundle.keys()) if default_bundle.get(key) != harsh_bundle.get(key)]
    if not deltas:
        return False, "hardcore bundle must differ from default bundle by parameter values"
    return True, "survival/hardcore delta-only contract preserved"


def _case_bundle_not_installed_refusal(repo_root: str):
    refusal_text = _read_text(os.path.join(repo_root, REFUSAL_REL))
    registry_text = _read_text(os.path.join(repo_root, REGISTRY_REL))
    for marker, rel in (
        ("CLIENT_SESSION_REFUSE_PACK_MISSING", REFUSAL_REL),
        ("refuse.pack_missing", REGISTRY_REL),
    ):
        text = refusal_text if rel == REFUSAL_REL else registry_text
        if marker not in text:
            return False, "missing marker {} in {}".format(marker, rel.replace("\\", "/"))
    return True, "bundle-not-installed refusal wiring present"


CASE_HANDLERS = {
    "profile_switch_requires_restart": _case_profile_switch_requires_restart,
    "remove_optional_bundle_core_boots": _case_remove_optional_bundle_core_boots,
    "survival_to_creative_transition": _case_survival_to_creative_transition,
    "survival_hardcore_delta_only": _case_survival_hardcore_delta_only,
    "bundle_not_installed_refusal": _case_bundle_not_installed_refusal,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Systemic stress checks for profile switching and optional bundles.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--case", choices=sorted(CASE_HANDLERS.keys()), required=True)
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    ok, message = CASE_HANDLERS[args.case](repo_root)
    if not ok:
        print("profile-bundle stress case {} failed: {}".format(args.case, message))
        return 1
    print("profile-bundle stress case {} OK: {}".format(args.case, message))
    return 0


if __name__ == "__main__":
    sys.exit(main())
