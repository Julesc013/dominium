"""STRICT test: RepoX negative invariant rules emit deterministic findings for violating fixtures."""

from __future__ import annotations

import os
import shutil
import sys
import tempfile


TEST_ID = "testx.repox.negative_invariants_smoke"
TEST_TAGS = ["strict", "repox", "smoke"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.repox.check import run_repox_check

    temp_root = tempfile.mkdtemp(prefix="xstack_repox_negative_")
    try:
        paths_and_lines = [
            (
                os.path.join(temp_root, "engine", "bad_pack_read.c"),
                'void x(){ FILE* f = fopen("packs/core/pack.json","r"); }\n',
            ),
            (
                os.path.join(temp_root, "game", "bad_schema_read.py"),
                'payload = open("schemas/session_spec.schema.json", "r", encoding="utf-8").read()\n',
            ),
            (
                os.path.join(temp_root, "client", "presentation", "bad_ui_call.py"),
                "result = run_process('process.camera_teleport')\n",
            ),
            (
                os.path.join(temp_root, "tools", "launcher", "bad_stage_arg.py"),
                'parser.add_argument("--from-stage")\n',
            ),
            (
                os.path.join(temp_root, "tools", "xstack", "pack_loader", "bad_contract_literal.py"),
                'token = "dom.contract.mass_conservation"\n',
            ),
            (
                os.path.join(temp_root, "server", "bad_control_mutation.py"),
                'state["control_bindings"] = []\n',
            ),
            (
                os.path.join(temp_root, "engine", "bad_player_literal.cpp"),
                'const char* who = "player.main";\n',
            ),
        ]
        for abs_path, line in paths_and_lines:
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(line)

        result = run_repox_check(repo_root=temp_root, profile="STRICT")
        findings = list(result.get("findings") or [])
        rule_ids = sorted(set(str(row.get("rule_id", "")) for row in findings))
        required = {
            "INV-NO-DIRECT-PACK-READS-IN-RUNTIME",
            "INV-NO-DIRECT-SCHEMA-PARSE-OUTSIDE-VALIDATION",
            "INV-UI-COMMAND-GRAPH-ONLY",
            "INV-NO-SESSION-PIPELINE-BYPASS",
            "INV-NO-HARDCODED-CONTRACT-TOKENS",
            "INV-CONTROL-PROCESSES-ONLY",
            "INV-NO-HARDCODED-PLAYER",
            "INV-CONTROL-ENTITLEMENT-GATED",
            "INV-MOVE-USES-BODY_MOVE_ATTEMPT",
            "INV-OWNERSHIP-CHECK-REQUIRED",
            "INV-VIEW-MODES-REGISTRY-DRIVEN",
            "INV-WATERMARK-ENFORCED",
            "INV-NO-COSMETIC-SEMANTICS",
            "INV-REPRESENTATION-RENDER-ONLY",
        }
        missing = sorted(rule for rule in required if rule not in rule_ids)
        if missing:
            return {"status": "fail", "message": "missing expected negative invariant finding(s): {}".format(",".join(missing))}
        return {"status": "pass", "message": "negative invariant smoke checks passed"}
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
