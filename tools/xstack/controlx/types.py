"""Shared data contracts for deterministic XStack orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


VALID_STEP_STATUS = ("pass", "fail", "refusal", "error")


@dataclass
class RunContext:
    repo_root: str
    profile: str
    cache_enabled: bool
    shards: int
    shard_index: int
    output_dir: str
    skip_testx: bool = False


@dataclass
class StepResult:
    step_id: str
    subsystem: str
    status: str
    message: str
    duration_ms: int
    findings: List[Dict[str, object]] = field(default_factory=list)
    artifacts: List[Dict[str, str]] = field(default_factory=list)

