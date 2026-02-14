"""Canonical runner protocol for XStack adapters."""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Sequence


@dataclass(frozen=True)
class RunnerContext:
    """Execution context passed to a runner."""

    repo_root: str
    workspace_id: str
    gate_command: str
    node: Dict[str, object]
    plan_profile: str
    repo_state_hash: str


@dataclass(frozen=True)
class RunnerResult:
    """Normalized runner execution result."""

    runner_id: str
    exit_code: int
    output: str
    artifacts_produced: Sequence[str]
    output_hash: str
    timestamp_utc: str


class BaseRunner(metaclass=ABCMeta):
    """Shared protocol implemented by all XStack runners."""

    @abstractmethod
    def runner_id(self) -> str:
        """Return canonical runner id."""

    @abstractmethod
    def input_hash(self, repo_state: str, registries_hash: str, profile: str) -> str:
        """Return deterministic input hash key for runner-specific cache context."""

    @abstractmethod
    def produces(self) -> List[str]:
        """Return canonical artifacts produced by this runner family."""

    @abstractmethod
    def run(self, context: RunnerContext) -> RunnerResult:
        """Execute runner work and return normalized result."""

    def supports_groups(self) -> bool:
        """Return whether runner can execute grouped sub-runs."""

        return False

    def estimate_cost(self, context: RunnerContext) -> int:
        """Return deterministic work-unit estimate."""

        _ = context
        return 1

    def default_full_enabled(self) -> bool:
        """Return true if runner is part of default FULL profile."""

        return False
