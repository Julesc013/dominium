import os
import shutil
import tempfile


def make_temp_repo_fixture(source_repo_root: str) -> str:
    tmp = tempfile.mkdtemp(prefix="registry_compile_fixture_")
    testdata_root = os.path.join(source_repo_root, "tools", "xstack", "testdata")
    for name in ("packs", "bundles", "session", "ui"):
        src_path = os.path.join(testdata_root, name)
        if not os.path.isdir(src_path):
            continue
        shutil.copytree(src_path, os.path.join(tmp, name))
    src_registries = os.path.join(testdata_root, "registries")
    if os.path.isdir(src_registries):
        shutil.copytree(src_registries, os.path.join(tmp, "data", "registries"))
    return tmp

