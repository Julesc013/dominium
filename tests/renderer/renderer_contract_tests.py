import argparse
import os


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        return handle.read()


def assert_contains(text, needle, label):
    if needle not in text:
        raise AssertionError("missing {}: {}".format(label, needle))


def test_renderer_doc(repo_root):
    doc_path = os.path.join(repo_root, "docs", "architecture", "RENDERER_RESPONSIBILITY.md")
    if not os.path.isfile(doc_path):
        raise AssertionError("missing renderer responsibility doc")
    text = read_text(doc_path)
    required_sections = [
        "Renderer Responsibility",
        "Required Renderer Backends",
        "Null renderer",
        "Software renderer",
        "GPU renderers",
        "Bare‑metal",
        "UI & Presentation Model",
        "Asset Handling",
        "Signal & Field Visualization",
        "Performance & Scaling",
        "Freeze & Lock",
    ]
    for section in required_sections:
        assert_contains(text, section, "renderer doc section")

    backends = ["OpenGL", "Vulkan", "Direct3D", "Metal"]
    for backend in backends:
        assert_contains(text, backend, "renderer backend")

    assert_contains(text, "client.ui", "capability scope")


def test_locklist(repo_root):
    path = os.path.join(repo_root, "docs", "architecture", "LOCKLIST.md")
    text = read_text(path)
    assert_contains(text, "Renderer layer", "locklist renderer entry")


def test_null_renderer_backend(repo_root):
    gfx = os.path.join(repo_root, "engine", "render", "d_gfx.c")
    if not os.path.isfile(gfx):
        raise AssertionError("missing renderer implementation")
    text = read_text(gfx)
    assert_contains(text, "DGFX_BACKEND_NULL", "null renderer backend")
    assert_contains(text, "\"null\"", "null renderer name")


def test_headless_flag(repo_root):
    launcher_cli = os.path.join(repo_root, "launcher", "cli", "launcher_cli_main.c")
    text = read_text(launcher_cli)
    assert_contains(text, "--headless", "headless flag")
    assert_contains(text, "--ui=none", "ui none flag")


def main():
    parser = argparse.ArgumentParser(description="Renderer contract tests")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    test_renderer_doc(repo_root)
    test_locklist(repo_root)
    test_null_renderer_backend(repo_root)
    test_headless_flag(repo_root)

    print("RENDERER-PERFECT-0 contract tests OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
