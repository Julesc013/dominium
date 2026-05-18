"""Temporary runtime control-plane import surface after MOVE-ROUTER-01.

MOVE-ROUTER-02 keeps runtime/game modules off ``tools.governance`` while the
underlying control-plane implementation is split in a later owner-specific task.
New runtime code should import from this package, not from ``tools.governance``.
"""

from tools.governance import *  # noqa: F401,F403
