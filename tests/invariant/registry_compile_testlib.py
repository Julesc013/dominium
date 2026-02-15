import os
import shutil
import tempfile


def make_temp_repo_fixture(source_repo_root: str) -> str:
    tmp = tempfile.mkdtemp(prefix="registry_compile_fixture_")
    src_packs = os.path.join(source_repo_root, "tools", "xstack", "testdata", "packs")
    dst_packs = os.path.join(tmp, "packs")
    shutil.copytree(src_packs, dst_packs)
    return tmp

