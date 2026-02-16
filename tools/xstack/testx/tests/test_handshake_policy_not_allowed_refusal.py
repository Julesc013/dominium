"""STRICT test: handshake policy-not-allowed refusal contract remains deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.handshake_policy_not_allowed_refusal"
TEST_TAGS = ["strict", "net", "security", "multiplayer"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.test_handshake_refuse_policy_not_allowed import run as existing_run

    return existing_run(repo_root)

