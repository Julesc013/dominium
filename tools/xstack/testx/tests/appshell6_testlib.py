"""APPSHELL-6 TestX helpers."""

from __future__ import annotations

import os
import sys


def ensure_repo_on_path(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)


def build_run_spec(repo_root: str, *, seed: str = "seed.appshell6.test", policy_id: str = "supervisor.policy.default", topology: str = "singleplayer") -> dict:
    ensure_repo_on_path(repo_root)
    from src.appshell.supervisor import build_supervisor_run_spec

    return build_supervisor_run_spec(
        repo_root=repo_root,
        seed=str(seed).strip() or "seed.appshell6.test",
        supervisor_policy_id=str(policy_id).strip() or "supervisor.policy.default",
        topology=str(topology).strip() or "singleplayer",
    )


def run_probe(repo_root: str, *, suffix: str = "default") -> dict:
    ensure_repo_on_path(repo_root)
    from tools.appshell.appshell6_probe import run_supervisor_probe

    return run_supervisor_probe(repo_root, suffix=str(suffix).strip() or "default")


def replay_probe(repo_root: str, *, suffix: str = "replay") -> dict:
    ensure_repo_on_path(repo_root)
    from tools.appshell.appshell6_probe import verify_supervisor_replay

    return verify_supervisor_replay(repo_root, suffix=str(suffix).strip() or "replay")


def build_hardening_report(repo_root: str) -> dict:
    ensure_repo_on_path(repo_root)
    from tools.appshell.supervisor_hardening_common import build_supervisor_hardening_report

    return build_supervisor_hardening_report(repo_root)


def canonicalize_sample_args(repo_root: str) -> dict:
    ensure_repo_on_path(repo_root)
    from src.appshell.supervisor import canonicalize_args

    return canonicalize_args(
        positional=["tools/appshell/supervisor_service.py"],
        flag_pairs=(
            ("--topology", "singleplayer"),
            ("--seed", "seed.sample"),
            ("--repo-root", "."),
            ("--contract-bundle-hash", "0" * 64),
        ),
    )


def run_local_engine(repo_root: str, *, seed: str = "seed.appshell6.engine", policy_id: str = "supervisor.policy.default", topology: str = "singleplayer"):
    ensure_repo_on_path(repo_root)
    from src.appshell.supervisor import SupervisorEngine

    run_spec = build_run_spec(repo_root, seed=seed, policy_id=policy_id, topology=topology)
    engine = SupervisorEngine(repo_root=repo_root, run_spec=run_spec)
    started = engine.start()
    return run_spec, engine, started
