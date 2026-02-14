"""Example extension hook for XStack integrators."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import List

from tools.xstack.core.runners_base import BaseRunner, RunnerContext, RunnerResult


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class ExampleXRunner(BaseRunner):
    def runner_id(self) -> str:
        return "examplex_runner"

    def input_hash(self, repo_state: str, registries_hash: str, profile: str) -> str:
        payload = {
            "runner_id": self.runner_id(),
            "repo_state": str(repo_state),
            "registries_hash": str(registries_hash),
            "profile": str(profile),
        }
        return _hash_text(json.dumps(payload, sort_keys=True, separators=(",", ":")))

    def produces(self) -> List[str]:
        return ["docs/audit/examplex/EXAMPLEX_REPORT.json"]

    def run(self, context: RunnerContext) -> RunnerResult:
        _ = context
        return RunnerResult(
            runner_id=self.runner_id(),
            exit_code=0,
            output="examplex.noop",
            artifacts_produced=self.produces(),
            output_hash=_hash_text("examplex.noop"),
            timestamp_utc=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            failure_class="",
            failure_message="ok",
            remediation_hint="",
        )

    def version_hash(self) -> str:
        payload = {
            "runner_id": self.runner_id(),
            "version": "1.0.0",
            "artifact_contract": self.produces(),
        }
        return _hash_text(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def register_extensions():
    return [
        {
            "extension_id": "example_x",
            "runner": ExampleXRunner(),
            "artifact_contract": ["docs/audit/examplex/EXAMPLEX_REPORT.json"],
            "scope_subtrees": ["tools", "docs"],
            "cost_class": "low",
        }
    ]
