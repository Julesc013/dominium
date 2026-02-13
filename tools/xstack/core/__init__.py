"""XStack incremental gate execution core."""

from .plan import build_execution_plan
from .scheduler import execute_plan

__all__ = [
    "build_execution_plan",
    "execute_plan",
]
