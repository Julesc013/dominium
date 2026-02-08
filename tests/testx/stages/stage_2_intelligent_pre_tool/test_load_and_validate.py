import os
import sys

HERE = os.path.abspath(os.path.dirname(__file__))
TESTX_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
if TESTX_ROOT not in sys.path:
    sys.path.insert(0, TESTX_ROOT)

from capability_suite_runner import run_suite


if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
    sys.exit(run_suite(repo_root, "CAPSET_WORLD_LIFE_INTELLIGENT", "test_load_and_validate"))
