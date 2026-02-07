import os
import sys

HERE = os.path.abspath(os.path.dirname(__file__))
TESTX_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
if TESTX_ROOT not in sys.path:
    sys.path.insert(0, TESTX_ROOT)

from stage_suite_runner import run_suite


if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
    sys.exit(run_suite(repo_root, "STAGE_0_NONBIO_WORLD", "test_command_surface"))
