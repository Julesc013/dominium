"""FAST test: explain artifact redaction follows epistemic policy tiers deterministically."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_explain_redaction_policy"
TEST_TAGS = ["fast", "meta", "contracts", "explain", "epistemic"]


_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from meta.explain import build_explain_artifact, redact_explain_artifact

    base = build_explain_artifact(
        explain_id="explain.test.redaction.001",
        event_id="event.therm.overheat.001",
        cause_chain=[
            "cause.temperature",
            "cause.flow_loss",
            "cause.maintenance_delay",
            "cause.policy.trip",
            "cause.hazard.overtemp",
        ],
        referenced_artifacts=[
            "artifact.decision:decision.1",
            "artifact.record:event.1",
            "artifact.record:event.2",
            "artifact.record:event.3",
            "artifact.record:event.4",
        ],
        remediation_hints=[
            "hint.increase.cooling",
            "hint.reduce.heat_input",
            "hint.inspect.thermal_path",
            "hint.perform.maintenance",
            "hint.verify.sensor",
        ],
        extensions={"event_kind_id": "therm.overheat"},
    )
    if not base:
        return {"status": "fail", "message": "base explain artifact could not be built"}

    micro = redact_explain_artifact(
        explain_artifact_row=base,
        epistemic_policy_id="policy.epistemic.observer",
        policy_row={"max_inspection_level": "micro"},
    )
    meso = redact_explain_artifact(
        explain_artifact_row=base,
        epistemic_policy_id="policy.epistemic.player",
        policy_row={"max_inspection_level": "meso"},
    )
    macro = redact_explain_artifact(
        explain_artifact_row=base,
        epistemic_policy_id="policy.epistemic.public",
        policy_row={"max_inspection_level": "macro"},
    )

    if len(list(micro.get("cause_chain") or [])) != len(list(base.get("cause_chain") or [])):
        return {"status": "fail", "message": "micro redaction should preserve full cause chain"}
    if len(list(meso.get("cause_chain") or [])) > 4:
        return {"status": "fail", "message": "meso redaction should truncate cause chain to <= 4"}
    if list(macro.get("cause_chain") or []) != ["cause.redacted"]:
        return {"status": "fail", "message": "macro redaction should mask cause_chain"}
    if list(macro.get("referenced_artifacts") or []):
        return {"status": "fail", "message": "macro redaction should clear referenced_artifacts"}

    modes = [
        str((dict(micro.get("extensions") or {})).get("redaction_mode", "")).strip(),
        str((dict(meso.get("extensions") or {})).get("redaction_mode", "")).strip(),
        str((dict(macro.get("extensions") or {})).get("redaction_mode", "")).strip(),
    ]
    if modes != ["none", "meso_truncate", "macro_mask"]:
        return {"status": "fail", "message": "unexpected redaction modes: {}".format(",".join(modes))}

    for row in (micro, meso, macro):
        fingerprint = str(row.get("deterministic_fingerprint", "")).strip().lower()
        if not _SHA256.fullmatch(fingerprint):
            return {"status": "fail", "message": "redacted explain artifact has invalid deterministic_fingerprint"}
    return {"status": "pass", "message": "explain redaction policy deterministic and tier-correct"}

