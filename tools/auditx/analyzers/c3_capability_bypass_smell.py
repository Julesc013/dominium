"""C3 Capability bypass smell analyzer."""

import os

from analyzers.base import make_finding


ANALYZER_ID = "C3_CAPABILITY_BYPASS_SMELL"


def _read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    bridge_rel = "client/core/client_command_bridge.c"
    bridge_text = _read_text(os.path.join(repo_root, bridge_rel.replace("/", os.sep)))
    if not bridge_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="capability_bypass_smell",
                severity="RISK",
                confidence=0.85,
                file_path=bridge_rel,
                evidence=["Missing client command bridge source; capability gates cannot be proven."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-UI-ENTITLEMENT-GATING"],
                related_paths=[bridge_rel],
            )
        )
        return findings

    required_tokens = (
        "client_command_capabilities_allowed(",
        "entitlement_allowed(",
        "refuse.entitlement_required",
        "refuse.profile_not_selected",
    )
    missing = [token for token in required_tokens if token not in bridge_text]
    if missing:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="capability_bypass_smell",
                severity="RISK",
                confidence=0.82,
                file_path=bridge_rel,
                evidence=[
                    "Bridge is missing required capability/entitlement guard markers.",
                    "Missing markers: {}".format(", ".join(missing)),
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_TEST",
                related_invariants=["INV-UI-ENTITLEMENT-GATING", "INV-COMMAND-CAPABILITY-DECLARED"],
                related_paths=[bridge_rel],
            )
        )

    registry_rel = "client/core/client_commands_registry.c"
    registry_text = _read_text(os.path.join(repo_root, registry_rel.replace("/", os.sep)))
    if not registry_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="capability_bypass_smell",
                severity="WARN",
                confidence=0.80,
                file_path=registry_rel,
                evidence=["Missing command registry source; entitlement metadata cannot be audited."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="DOC_FIX",
                related_invariants=["INV-UI-ENTITLEMENT-GATING"],
                related_paths=[registry_rel],
            )
        )
        return findings

    required_commands = (
        "client.ui.hud.show",
        "client.ui.overlay.world_layers.show",
        "client.console.open",
        "client.console.open.readwrite",
        "client.camera.freecam.enable",
    )
    for command_id in required_commands:
        if command_id not in registry_text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="capability_bypass_smell",
                    severity="WARN",
                    confidence=0.75,
                    file_path=registry_rel,
                    evidence=[
                        "Entitlement-sensitive command missing from canonical command registry.",
                        "Missing command: {}".format(command_id),
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-UI-ENTITLEMENT-GATING"],
                    related_paths=[registry_rel],
                )
            )
    return findings
