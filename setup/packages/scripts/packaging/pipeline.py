#!/usr/bin/env python3
from __future__ import print_function

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys


def _repo_root_from_script():
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.normpath(os.path.join(here, os.pardir, os.pardir))


def _is_windows():
    return os.name == "nt"


def _exe_suffix():
    return ".exe" if _is_windows() else ""


def _source_date_epoch(reproducible):
    v = os.environ.get("SOURCE_DATE_EPOCH", "").strip()
    if not v:
        if reproducible:
            raise SystemExit("SOURCE_DATE_EPOCH is required in --reproducible mode")
        return 0
    try:
        return int(v)
    except Exception:
        raise SystemExit("invalid SOURCE_DATE_EPOCH: %r" % v)


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _norm_rel(path):
    path = path.replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    while path.startswith("/"):
        path = path[1:]
    return path


def _walk_files(root_dir):
    root_dir = os.path.abspath(root_dir)
    rels = []
    for cur_root, cur_dirs, cur_files in os.walk(root_dir):
        cur_dirs.sort()
        cur_files.sort()
        rel_root = os.path.relpath(cur_root, root_dir)
        rel_root = "" if rel_root == "." else _norm_rel(rel_root)
        for fn in cur_files:
            rel = _norm_rel(os.path.join(rel_root, fn))
            rels.append(rel)
    return sorted(set(rels))


def _touch_tree(root_dir, epoch):
    if epoch <= 0:
        return
    root_dir = os.path.abspath(root_dir)
    for cur_root, cur_dirs, cur_files in os.walk(root_dir):
        for fn in cur_files:
            p = os.path.join(cur_root, fn)
            try:
                os.utime(p, (epoch, epoch))
            except Exception:
                pass
        for d in cur_dirs:
            p = os.path.join(cur_root, d)
            try:
                os.utime(p, (epoch, epoch))
            except Exception:
                pass
    try:
        os.utime(root_dir, (epoch, epoch))
    except Exception:
        pass


def _load_cmake_cache(build_dir):
    cache = {}
    path = os.path.join(os.path.abspath(build_dir), "CMakeCache.txt")
    if not os.path.isfile(path):
        return cache
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("//") or line.startswith("#"):
                continue
            # KEY:TYPE=VALUE
            if ":" not in line or "=" not in line:
                continue
            key, rest = line.split(":", 1)
            _typ, val = rest.split("=", 1)
            cache[key.strip()] = val.strip()
    return cache


def _walk_candidates(root_dir, want_name_lower):
    for cur_root, dirs, files in os.walk(root_dir):
        base = os.path.basename(cur_root)
        if base in ("CMakeFiles", "Testing", ".git", ".idea", ".vscode", ".cmake", "_deps"):
            dirs[:] = []
            continue
        for fn in files:
            if fn.lower() == want_name_lower:
                yield os.path.join(cur_root, fn)


def _find_unique_file(root_dir, filename, prefer_subpaths=None):
    want = filename.lower()
    hits = list(_walk_candidates(root_dir, want))
    if not hits:
        raise RuntimeError("not found: %s under %s" % (filename, root_dir))
    if prefer_subpaths:
        for needle in prefer_subpaths:
            preferred = [p for p in hits if needle.replace("\\", "/").lower() in p.replace("\\", "/").lower()]
            if len(preferred) == 1:
                return preferred[0]
            if len(preferred) > 1:
                hits = preferred
    if len(hits) == 1:
        return hits[0]
    raise RuntimeError("ambiguous (%d matches) for %s under %s:\n%s"
                       % (len(hits), filename, root_dir, "\n".join(sorted(hits)[:50])))


def _try_find_unique_file(root_dir, filename, prefer_subpaths=None):
    try:
        return _find_unique_file(root_dir, filename, prefer_subpaths=prefer_subpaths)
    except Exception:
        return None


def _copy_exe_and_sidecars(src_exe, dst_dir, copy_exe=True, copy_sidecars=True):
    os.makedirs(dst_dir, exist_ok=True)
    if copy_exe:
        shutil.copy2(src_exe, os.path.join(dst_dir, os.path.basename(src_exe)))

    if not copy_sidecars:
        return

    src_dir = os.path.dirname(src_exe)
    if _is_windows():
        exts = [".dll"]
    elif sys.platform == "darwin":
        exts = [".dylib"]
    else:
        exts = [".so"]

    for fn in sorted(os.listdir(src_dir)):
        low = fn.lower()
        if any(low.endswith(e) for e in exts) or low.endswith(".so.0") or ".so." in low:
            p = os.path.join(src_dir, fn)
            if os.path.isfile(p):
                shutil.copy2(p, os.path.join(dst_dir, fn))


def _run(cmd, env=None, cwd=None):
    sys.stdout.flush()
    subprocess.check_call(cmd, env=env, cwd=cwd)


def _make_deterministic_zip(repo_root, input_dir, output_path, epoch):
    py = sys.executable
    script = os.path.join(repo_root, "scripts", "packaging", "make_deterministic_archive.py")
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = str(int(epoch))
    _run([py, script, "--format", "zip", "--input", input_dir, "--output", output_path, "--root-name", "."], env=env)


def _make_deterministic_archive(repo_root, fmt, input_dir, output_path, root_name, epoch):
    py = sys.executable
    script = os.path.join(repo_root, "scripts", "packaging", "make_deterministic_archive.py")
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = str(int(epoch))
    _run([py, script, "--format", fmt, "--input", input_dir, "--output", output_path, "--root-name", root_name], env=env)


def _write_text(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path, obj):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, sort_keys=True, indent=2)
        f.write("\n")


def _fill_payload_digests(manifest_obj, artifact_dir):
    # Updates payload entries with sha256/size when values are "AUTO".
    for comp in manifest_obj.get("components", []) or []:
        for p in comp.get("payloads", []) or []:
            rel = (p.get("path") or "").replace("\\", "/").strip()
            if not rel:
                continue
            abs_p = os.path.join(artifact_dir, rel.replace("/", os.sep))

            if os.path.isdir(abs_p):
                if str(p.get("sha256", "")).strip().lower() in ("auto", "") or str(p.get("size", "")).strip().lower() in ("auto", ""):
                    files = []
                    total = 0
                    for cur_root, cur_dirs, cur_files in os.walk(abs_p):
                        cur_dirs.sort()
                        cur_files.sort()
                        rel_root = os.path.relpath(cur_root, abs_p)
                        rel_root = "" if rel_root == "." else _norm_rel(rel_root)
                        for fn in cur_files:
                            rp = _norm_rel(os.path.join(rel_root, fn))
                            ap = os.path.join(cur_root, fn)
                            total += os.path.getsize(ap)
                            files.append((rp, _sha256_file(ap)))
                    files.sort()
                    digest_lines = ["%s  %s\n" % (sha, rp) for (rp, sha) in files]
                    root_sha = hashlib.sha256("".join(digest_lines).encode("utf-8")).hexdigest()
                    if str(p.get("sha256", "")).strip().lower() in ("auto", ""):
                        p["sha256"] = root_sha
                    if str(p.get("size", "")).strip().lower() in ("auto", ""):
                        p["size"] = int(total)
                continue

            if not os.path.isfile(abs_p):
                raise RuntimeError("payload not found for manifest: %s" % rel)
            if str(p.get("sha256", "")).strip().lower() in ("auto", ""):
                p["sha256"] = _sha256_file(abs_p)
            if str(p.get("size", "")).strip().lower() in ("auto", ""):
                p["size"] = os.path.getsize(abs_p)


def _validate_manifest_payloads(manifest_obj, artifact_dir):
    bad = []
    for comp in manifest_obj.get("components", []) or []:
        cid = comp.get("component_id", "")
        for p in comp.get("payloads", []) or []:
            rel = (p.get("path") or "").replace("\\", "/").strip()
            want = (p.get("sha256") or "").strip().lower()
            if not rel:
                continue
            abs_p = os.path.join(artifact_dir, rel.replace("/", os.sep))
            if os.path.isdir(abs_p):
                files = []
                for cur_root, cur_dirs, cur_files in os.walk(abs_p):
                    cur_dirs.sort()
                    cur_files.sort()
                    rel_root = os.path.relpath(cur_root, abs_p)
                    rel_root = "" if rel_root == "." else _norm_rel(rel_root)
                    for fn in cur_files:
                        rp = _norm_rel(os.path.join(rel_root, fn))
                        ap = os.path.join(cur_root, fn)
                        files.append((rp, _sha256_file(ap)))
                files.sort()
                digest_lines = ["%s  %s\n" % (sha, rp) for (rp, sha) in files]
                got = hashlib.sha256("".join(digest_lines).encode("utf-8")).hexdigest()
                if got.lower() != want.lower():
                    bad.append((cid, rel, "sha256 mismatch: %s != %s" % (got, want)))
                continue
            if not os.path.isfile(abs_p):
                bad.append((cid, rel, "missing"))
                continue
            got = _sha256_file(abs_p)
            if got.lower() != want.lower():
                bad.append((cid, rel, "sha256 mismatch: %s != %s" % (got, want)))
    if bad:
        msg = ["manifest->payload validation failed:"]
        for cid, rel, err in bad:
            msg.append("  %s: %s: %s" % (cid, rel, err))
        raise RuntimeError("\n".join(msg))


def _manifest_validate_details(setup_bin, manifest_path):
    # Best-effort JSON parse across CLI schema iterations.
    try:
        out = subprocess.check_output([setup_bin, "manifest", "validate", "--in", manifest_path, "--json"])
    except Exception:
        return {}
    try:
        s = out.decode("utf-8", errors="ignore").strip()
        obj = json.loads(s)
    except Exception:
        return {}

    if isinstance(obj, dict) and "details" in obj and isinstance(obj["details"], dict):
        d = obj["details"]
        return {
            "content_digest32": d.get("content_digest32"),
            "content_digest64": d.get("content_digest64"),
        }
    if isinstance(obj, dict):
        return {
            "content_digest32": obj.get("content_digest32"),
            "content_digest64": obj.get("content_digest64"),
        }
    return {}


def _write_artifact_digests(artifact_dir, build_cache, version, epoch, reproducible, manifest_details):
    rel_files = _walk_files(artifact_dir)

    digest_lines = []
    file_entries = []
    for rel in rel_files:
        abs_p = os.path.join(artifact_dir, rel.replace("/", os.sep))
        sha = _sha256_file(abs_p)
        size = os.path.getsize(abs_p)
        digest_lines.append("%s  %s\n" % (sha, rel))
        file_entries.append({"path": rel, "sha256": sha, "size": int(size)})

    sums_path = os.path.join(artifact_dir, "setup", "SHA256SUMS")
    _write_text(sums_path, "".join(digest_lines))

    exclude = set([
        _norm_rel(os.path.relpath(sums_path, artifact_dir)),
        "setup/artifact_manifest.json",
    ])
    layout_lines = []
    for ent in file_entries:
        if ent["path"] in exclude:
            continue
        layout_lines.append("%s  %s\n" % (ent["sha256"], ent["path"]))
    layout_sha = hashlib.sha256("".join(layout_lines).encode("utf-8")).hexdigest()

    manifest_path = os.path.join(artifact_dir, "setup", "manifests", "product.dsumanifest")
    manifest_rel = _norm_rel(os.path.relpath(manifest_path, artifact_dir))
    manifest_sha = _sha256_file(manifest_path)

    out = {
        "schema_version": 1,
        "artifact_version": version,
        "source_date_epoch": int(epoch),
        "reproducible_mode": 1 if reproducible else 0,
        "build": {
            "dom_build_id": build_cache.get("DOM_BUILD_ID", ""),
            "dom_toolchain_id": build_cache.get("DOM_TOOLCHAIN_ID", ""),
            "cmake_generator": build_cache.get("CMAKE_GENERATOR", ""),
            "cmake_version": build_cache.get("CMAKE_VERSION", ""),
            "c_compiler": build_cache.get("CMAKE_C_COMPILER", ""),
            "cxx_compiler": build_cache.get("CMAKE_CXX_COMPILER", ""),
        },
        "compression": {
            "portable_archives": [
                {"format": "zip", "method": "stored", "root_name": "artifact_root", "source_date_epoch": int(epoch)},
                {"format": "tar.gz", "gzip_mtime": int(epoch), "root_name": "artifact_root", "source_date_epoch": int(epoch)},
            ],
        },
        "product_manifest": {
            "path": manifest_rel,
            "sha256": manifest_sha,
            "content_digest32": manifest_details.get("content_digest32", ""),
            "content_digest64": manifest_details.get("content_digest64", ""),
        },
        "layout_sha256": layout_sha,
        "files": file_entries,
    }

    out_path = os.path.join(artifact_dir, "setup", "artifact_manifest.json")
    _write_json(out_path, out)


def assemble_artifact(args):
    repo_root = _repo_root_from_script()
    epoch = _source_date_epoch(args.reproducible)

    out_dir = os.path.abspath(args.out)
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    # Canonical dirs.
    os.makedirs(os.path.join(out_dir, "setup", "manifests"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "setup", "policies"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "payloads", "launcher"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "payloads", "runtime"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "payloads", "tools"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "payloads", "packs"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "docs"), exist_ok=True)

    # Docs.
    license_src = os.path.join(repo_root, "LICENSE")
    if not os.path.exists(license_src):
        license_src = os.path.join(repo_root, "LICENSE.md")
    shutil.copy2(license_src, os.path.join(out_dir, "docs", "LICENSE"))
    shutil.copy2(os.path.join(repo_root, "README.md"), os.path.join(out_dir, "docs", "README"))
    _write_text(os.path.join(out_dir, "docs", "VERSION"), (args.version.strip() + "\n"))

    # Locate build outputs.
    build_dir = os.path.abspath(args.build_dir)
    setup_bin = _try_find_unique_file(build_dir, "dominium-setup" + _exe_suffix(), prefer_subpaths=["source/dominium/setup/"])
    if not setup_bin:
        setup_bin = _try_find_unique_file(build_dir, "dominium-setup" + _exe_suffix(), prefer_subpaths=["source/dominium/setup/"])
    if not setup_bin:
        legacy_bin = _try_find_unique_file(build_dir, "dominium-setup-legacy" + _exe_suffix(), prefer_subpaths=["source/dominium/setup/"])
        if not legacy_bin:
            legacy_bin = _try_find_unique_file(build_dir, "tool_setup" + _exe_suffix(), prefer_subpaths=["source/dominium/setup/"])
        if legacy_bin and not args.allow_legacy_setup:
            raise RuntimeError("legacy setup binary detected; rerun with --allow-legacy-setup to stage dominium-setup-legacy")
        setup_bin = legacy_bin
    if not setup_bin:
        raise RuntimeError("setup binary not found (dominium-setup or dominium-setup)")
    launcher_bin = _find_unique_file(build_dir, "dominium-launcher" + _exe_suffix(), prefer_subpaths=["source/dominium/launcher/"])
    game_bin = _find_unique_file(build_dir, "dominium_game" + _exe_suffix(), prefer_subpaths=["source/dominium/game/"])

    # Stage Setup Core binary into artifact_root/setup/.
    setup_dst = os.path.join(out_dir, "setup", os.path.basename(setup_bin))
    shutil.copy2(setup_bin, setup_dst)
    setup_base = os.path.basename(setup_bin).lower()
    setup_is_legacy = setup_base in (
        ("dominium-setup-legacy" + _exe_suffix()).lower(),
        ("tool_setup" + _exe_suffix()).lower(),
    )
    if not setup_is_legacy:
        setup_alias = os.path.join(out_dir, "setup", "dominium-setup" + _exe_suffix())
        if setup_base != ("dominium-setup" + _exe_suffix()).lower():
            shutil.copy2(setup_bin, setup_alias)

    # Stage setup CLI script (used by setup frontends for transactional ops).
    setup_cli_script = os.path.join(repo_root, "tools", "setup", "setup_cli.py")
    if os.path.isfile(setup_cli_script):
        shutil.copy2(setup_cli_script, os.path.join(out_dir, "setup", "setup_cli.py"))

    # Optional Linux setup frontends/adapters (best-effort copy when built).
    for extra in ("dominium-setup-tui", "dominium-setup-gui", "dominium-setup-linux", "dominium-setup-macos"):
        extra_bin = _try_find_unique_file(build_dir, extra + _exe_suffix(), prefer_subpaths=["source/dominium/setup/"])
        if extra_bin:
            shutil.copy2(extra_bin, os.path.join(out_dir, "setup", os.path.basename(extra_bin)))

    # Populate payload file trees (fileset payloads).
    # Avoid per-component file path collisions by placing shared runtime DLLs
    # in the runtime payload only. Launcher payload installs the launcher exe only.
    runtime_bin_dir = os.path.join(out_dir, "payloads", "runtime", "bin")
    launcher_bin_dir = os.path.join(out_dir, "payloads", "launcher", "bin")

    _copy_exe_and_sidecars(launcher_bin, launcher_bin_dir, copy_exe=True, copy_sidecars=False)

    _copy_exe_and_sidecars(game_bin, runtime_bin_dir, copy_exe=True, copy_sidecars=True)
    _copy_exe_and_sidecars(launcher_bin, runtime_bin_dir, copy_exe=False, copy_sidecars=True)

    os.makedirs(os.path.join(out_dir, "payloads", "tools", "tools"), exist_ok=True)
    _write_text(os.path.join(out_dir, "payloads", "tools", "tools", "README.txt"), "Dominium tools payload (placeholder)\n")

    src_pack = os.path.join(repo_root, "repo", "mods", "base_demo")
    dst_pack = os.path.join(out_dir, "payloads", "packs", "base", "repo", "mods", "base_demo")
    os.makedirs(os.path.dirname(dst_pack), exist_ok=True)
    shutil.copytree(src_pack, dst_pack)

    # Manifest: load template, fill payload digests, compile to DSUM.
    template_path = os.path.abspath(args.manifest_template)
    manifest_obj = _load_json(template_path)
    manifest_obj["product_version"] = args.version.strip()
    _fill_payload_digests(manifest_obj, out_dir)

    import dsumanifest
    payload = dsumanifest.compile_dsumanifest_from_json(manifest_obj)
    data = dsumanifest.wrap_payload_to_dsumanifest(payload)

    manifest_out = os.path.join(out_dir, "setup", "manifests", "product.dsumanifest")
    with open(manifest_out, "wb") as f:
        f.write(data)

    # Validate manifest loadable by Setup Core, and payload digests match.
    _validate_manifest_payloads(manifest_obj, out_dir)
    manifest_details = _manifest_validate_details(setup_bin, manifest_out)
    _run([setup_bin, "manifest", "validate", "--in", manifest_out])

    # Record artifact digests/toolchain identifiers.
    build_cache = _load_cmake_cache(build_dir)
    _write_artifact_digests(out_dir, build_cache, args.version.strip(), epoch, args.reproducible, manifest_details)

    if args.reproducible:
        _touch_tree(out_dir, epoch)

    print("assembled", out_dir)
    return 0


def package_portable(args):
    repo_root = _repo_root_from_script()
    epoch = _source_date_epoch(args.reproducible)

    artifact_dir = os.path.abspath(args.artifact)
    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    root_name = "artifact_root"
    zip_path = os.path.join(out_dir, "dominium-%s.zip" % args.version.strip())
    tgz_path = os.path.join(out_dir, "dominium-%s.tar.gz" % args.version.strip())

    _make_deterministic_archive(repo_root, "zip", artifact_dir, zip_path, root_name, epoch)
    _make_deterministic_archive(repo_root, "tar.gz", artifact_dir, tgz_path, root_name, epoch)

    print("wrote", zip_path)
    print("wrote", tgz_path)
    return 0


def _guid_from_md5(seed):
    h = hashlib.md5(seed.encode("utf-8")).hexdigest()
    return "{%s-%s-%s-%s-%s}" % (h[0:8], h[8:12], h[12:16], h[16:20], h[20:32])


def package_windows(args):
    if not _is_windows():
        raise SystemExit("windows packaging can only run on Windows hosts")

    epoch = _source_date_epoch(args.reproducible)

    artifact_dir = os.path.abspath(args.artifact)
    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    candle = shutil.which("candle")
    light = shutil.which("light")
    if not candle or not light:
        raise SystemExit("WiX candle/light not found in PATH (required for MSI/EXE packaging)")

    version = args.version.strip()
    manufacturer = "Dominium"
    license_file = os.path.join(_repo_root_from_script(), "scripts", "packaging", "windows", "license.rtf")

    upgrade_code = "{6BA5C836-8F7E-4C48-BC07-7AD1C0C83E74}"
    bundle_upgrade_code = "{5DD3A6BD-4F3B-4E0C-B5D1-0B2C879C98E3}"

    product_code = _guid_from_md5("dominium-setup-product-%s" % version)
    package_code = _guid_from_md5("dominium-setup-package-%s" % version)
    bundle_code = _guid_from_md5("dominium-setup-bundle-%s" % version)

    gen_wxs = os.path.join(out_dir, "DominiumSetup.generated.wxs")
    wixobj = os.path.join(out_dir, "DominiumSetup.wixobj")
    msi_path = os.path.join(out_dir, "DominiumSetup-%s.msi" % version)

    gen_script = os.path.join(_repo_root_from_script(), "scripts", "packaging", "windows", "generate_dominium_setup_wxs.py")
    _run([sys.executable, gen_script,
          "--artifact-dir", artifact_dir,
          "--out", gen_wxs,
          "--product-version", version,
          "--manufacturer", manufacturer,
          "--product-code", product_code,
          "--upgrade-code", upgrade_code,
          "--package-code", package_code,
          "--license-file", license_file])

    _run([candle,
          "-dArtifactDir=%s" % artifact_dir,
          "-out", wixobj,
          gen_wxs], env=dict(os.environ, SOURCE_DATE_EPOCH=str(int(epoch))))

    _run([light,
          "-ext", "WixUIExtension",
          "-ext", "WixUtilExtension",
          "-out", msi_path,
          wixobj], env=dict(os.environ, SOURCE_DATE_EPOCH=str(int(epoch))))

    print("wrote", msi_path)

    if args.bootstrapper:
        boot_wxs = os.path.join(_repo_root_from_script(), "scripts", "packaging", "windows", "bootstrapper.wxs")
        boot_obj = os.path.join(out_dir, "DominiumSetup.bootstrapper.wixobj")
        boot_path = os.path.join(out_dir, "DominiumSetup-%s.exe" % version)

        _run([candle,
              "-dProductVersion=%s" % version,
              "-dManufacturer=%s" % manufacturer,
              "-dLicenseFile=%s" % license_file,
              "-dBundleIcon=",
              "-dBundleLogo=",
              "-dBundleCode=%s" % bundle_code,
              "-dBundleUpgradeCode=%s" % bundle_upgrade_code,
              "-dMsiPath=%s" % msi_path,
              "-out", boot_obj,
              boot_wxs], env=dict(os.environ, SOURCE_DATE_EPOCH=str(int(epoch))), cwd=out_dir)

        _run([light,
              "-ext", "WixBalExtension",
              "-out", boot_path,
              boot_obj], env=dict(os.environ, SOURCE_DATE_EPOCH=str(int(epoch))), cwd=out_dir)

        print("wrote", boot_path)

    return 0


def _write_vdf(path, text):
    _write_text(path, text)


def package_steam(args):
    epoch = _source_date_epoch(args.reproducible)

    artifact_dir = os.path.abspath(args.artifact)
    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    appid = str(int(args.appid))
    depotid = str(int(args.depotid))

    depots_root = os.path.join(out_dir, "depots")
    depot_root = os.path.join(depots_root, depotid)
    if os.path.isdir(depot_root):
        shutil.rmtree(depot_root)
    os.makedirs(depots_root, exist_ok=True)
    shutil.copytree(artifact_dir, depot_root)

    buildoutput = os.path.join(out_dir, "build_output")
    os.makedirs(buildoutput, exist_ok=True)

    depot_vdf = os.path.join(out_dir, "depot_build_%s.vdf" % depotid)
    app_vdf = os.path.join(out_dir, "app_build.vdf")

    _write_vdf(depot_vdf,
               '"DepotBuildConfig"\n'
               '{\n'
               '  "DepotID" "%s"\n'
               '  "ContentRoot" "%s"\n'
               '  "FileMapping"\n'
               '  {\n'
               '    "LocalPath" "*"\n'
               '    "DepotPath" "."\n'
               '    "recursive" "1"\n'
               '  }\n'
               '}\n' % (depotid, depot_root.replace("\\", "/")))

    _write_vdf(app_vdf,
               '"appbuild"\n'
               '{\n'
               '  "appid" "%s"\n'
               '  "desc" "Dominium %s"\n'
               '  "buildoutput" "%s"\n'
               '  "contentroot" "%s"\n'
               '  "setlive" ""\n'
               '  "depots"\n'
               '  {\n'
               '    "%s" "%s"\n'
               '  }\n'
               '}\n' % (
                   appid,
                   args.version.strip(),
                   buildoutput.replace("\\", "/"),
                   out_dir.replace("\\", "/"),
                   depotid,
                   depot_vdf.replace("\\", "/"),
               ))

    if args.reproducible:
        _touch_tree(depot_root, epoch)

    print("staged depot", depot_root)
    print("wrote", depot_vdf)
    print("wrote", app_vdf)
    return 0


def package_macos(args):
    if sys.platform != "darwin":
        raise SystemExit("macos packaging can only run on macOS hosts")

    repo_root = _repo_root_from_script()
    epoch = _source_date_epoch(args.reproducible)

    artifact_dir = os.path.abspath(args.artifact)
    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    pkgbuild = shutil.which("pkgbuild")
    productbuild = shutil.which("productbuild")
    hdiutil = shutil.which("hdiutil")
    if not pkgbuild or not productbuild or not hdiutil:
        raise SystemExit("missing required macOS tools: pkgbuild/productbuild/hdiutil")

    version = args.version.strip()
    identifier = args.identifier.strip()

    work = os.path.join(out_dir, "_work_macos")
    if os.path.isdir(work):
        shutil.rmtree(work)
    os.makedirs(work, exist_ok=True)

    # Package root: stage artifact_root under /Library/Application Support/Dominium/artifact_root
    stage_root = os.path.join(work, "pkgroot")
    payload_root = os.path.join(stage_root, "Library", "Application Support", "Dominium", "artifact_root")
    os.makedirs(os.path.dirname(payload_root), exist_ok=True)
    shutil.copytree(artifact_dir, payload_root)

    scripts_dir = os.path.join(repo_root, "scripts", "packaging", "macos", "pkg_scripts")
    component_pkg = os.path.join(work, "Dominium-%s.component.pkg" % version)
    distribution_pkg = os.path.join(out_dir, "Dominium-%s.pkg" % version)

    env = dict(os.environ, SOURCE_DATE_EPOCH=str(int(epoch)))

    _run([pkgbuild,
          "--root", stage_root,
          "--identifier", identifier,
          "--version", version,
          "--install-location", "/",
          "--scripts", scripts_dir,
          component_pkg], env=env)

    _run([productbuild,
          "--identifier", identifier,
          "--version", version,
          "--package", component_pkg,
          distribution_pkg], env=env)

    dmg_path = os.path.join(out_dir, "Dominium-%s.dmg" % version)
    dmg_root = os.path.join(work, "dmgroot")
    os.makedirs(dmg_root, exist_ok=True)
    shutil.copy2(distribution_pkg, os.path.join(dmg_root, os.path.basename(distribution_pkg)))

    _run([hdiutil, "create",
          "-volname", "Dominium",
          "-srcfolder", dmg_root,
          "-ov",
          "-format", "UDZO",
          dmg_path], env=env)

    if args.reproducible:
        _touch_tree(work, epoch)

    print("wrote", distribution_pkg)
    print("wrote", dmg_path)
    return 0


def package_linux(args):
    if not sys.platform.startswith("linux"):
        raise SystemExit("linux packaging can only run on Linux hosts")

    repo_root = _repo_root_from_script()
    epoch = _source_date_epoch(args.reproducible)

    artifact_dir = os.path.abspath(args.artifact)
    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    version = args.version.strip()

    # Portable tarball (canonical layout inside: artifact_root/*).
    tar_path = os.path.join(out_dir, "dominium-%s.tar.gz" % version)
    _make_deterministic_archive(repo_root, "tar.gz", artifact_dir, tar_path, "artifact_root", epoch)
    print("wrote", tar_path)

    # Portable tarball wrapper (placed next to the tarball, not inside artifact_root/).
    wrapper_src = os.path.join(repo_root, "scripts", "packaging", "linux", "dominium-install.sh")
    wrapper_dst = os.path.join(out_dir, "dominium-install.sh")
    if os.path.isfile(wrapper_src):
        shutil.copy2(wrapper_src, wrapper_dst)
        try:
            os.chmod(wrapper_dst, 0o755)
        except Exception:
            pass
        print("wrote", wrapper_dst)

    dpkg_deb = shutil.which("dpkg-deb")
    rpmbuild = shutil.which("rpmbuild")

    if args.build_deb:
        if not dpkg_deb:
            raise SystemExit("dpkg-deb not found (required for .deb packaging)")
        deb_root = os.path.join(out_dir, "_work_deb", "root")
        if os.path.isdir(os.path.dirname(deb_root)):
            shutil.rmtree(os.path.dirname(deb_root))
        os.makedirs(os.path.join(deb_root, "DEBIAN"), exist_ok=True)

        stage = os.path.join(deb_root, "opt", "dominium", "artifact_root")
        os.makedirs(os.path.dirname(stage), exist_ok=True)
        shutil.copytree(artifact_dir, stage)

        def _subst(text):
            return (text.replace("@VERSION@", version)
                        .replace("@MAINTAINER@", args.maintainer)
                        .replace("@DEPENDS@", args.depends))

        ctrl_in = os.path.join(repo_root, "scripts", "packaging", "linux", "deb", "DEBIAN", "control.in")
        with open(ctrl_in, "r", encoding="utf-8") as f:
            ctrl = _subst(f.read())
        _write_text(os.path.join(deb_root, "DEBIAN", "control"), ctrl)

        for name in ("postinst", "prerm", "postrm"):
            src = os.path.join(repo_root, "scripts", "packaging", "linux", "deb", "DEBIAN", name)
            dst = os.path.join(deb_root, "DEBIAN", name)
            shutil.copy2(src, dst)
            os.chmod(dst, 0o755)

        deb_path = os.path.join(out_dir, "dominium-%s.deb" % version)
        _run([dpkg_deb, "--build", deb_root, deb_path], env=dict(os.environ, SOURCE_DATE_EPOCH=str(int(epoch))))
        print("wrote", deb_path)

    if args.build_rpm:
        if not rpmbuild:
            raise SystemExit("rpmbuild not found (required for .rpm packaging)")

        top = os.path.join(out_dir, "_work_rpm")
        for d in ("BUILD", "BUILDROOT", "RPMS", "SOURCES", "SPECS", "SRPMS"):
            os.makedirs(os.path.join(top, d), exist_ok=True)

        sources_dom = os.path.join(top, "SOURCES", "dominium", "artifact_root")
        if os.path.isdir(os.path.join(top, "SOURCES", "dominium")):
            shutil.rmtree(os.path.join(top, "SOURCES", "dominium"))
        os.makedirs(os.path.dirname(sources_dom), exist_ok=True)
        shutil.copytree(artifact_dir, sources_dom)

        spec_in = os.path.join(repo_root, "scripts", "packaging", "linux", "rpm", "dominium.spec.in")
        with open(spec_in, "r", encoding="utf-8") as f:
            spec = (f.read().replace("@VERSION@", version)
                            .replace("@RELEASE@", args.release)
                            .replace("@REQUIRES@", args.requires))
        spec_path = os.path.join(top, "SPECS", "dominium.spec")
        _write_text(spec_path, spec)

        _run([rpmbuild, "-bb", spec_path, "--define", "_topdir %s" % top],
             env=dict(os.environ, SOURCE_DATE_EPOCH=str(int(epoch))))

        # Best-effort: copy first resulting rpm to out_dir with canonical name.
        rpms_dir = os.path.join(top, "RPMS")
        rpm_out = None
        for cur_root, _dirs, files in os.walk(rpms_dir):
            for fn in sorted(files):
                if fn.endswith(".rpm"):
                    rpm_out = os.path.join(cur_root, fn)
                    break
            if rpm_out:
                break
        if not rpm_out:
            raise SystemExit("rpmbuild succeeded but no .rpm found under %s" % rpms_dir)
        rpm_path = os.path.join(out_dir, "dominium-%s.rpm" % version)
        shutil.copy2(rpm_out, rpm_path)
        print("wrote", rpm_path)

    return 0


def main(argv):
    ap = argparse.ArgumentParser(description="Dominium packaging pipeline (Plan S-8).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_asm = sub.add_parser("assemble", help="Assemble canonical artifact_root/ and record digests.")
    ap_asm.add_argument("--build-dir", required=True, help="CMake build directory containing built outputs")
    ap_asm.add_argument("--allow-legacy-setup", action="store_true",
                        help="Allow staging dominium-setup-legacy/tool_setup when setup is missing.")
    ap_asm.add_argument("--out", required=True, help="Output directory (artifact_root/)")
    ap_asm.add_argument("--version", required=True, help="Artifact/product version (x.y.z)")
    ap_asm.add_argument("--manifest-template", default=os.path.join("assets", "setup", "manifests", "product.template.json"),
                        help="Manifest JSON template (default: assets/setup/manifests/product.template.json)")
    ap_asm.add_argument("--reproducible", action="store_true", help="Enforce strict reproducible mode (requires SOURCE_DATE_EPOCH).")
    ap_asm.set_defaults(func=assemble_artifact)

    ap_port = sub.add_parser("portable", help="Create portable archives from an assembled artifact_root/.")
    ap_port.add_argument("--artifact", required=True, help="Input artifact_root/ directory")
    ap_port.add_argument("--out", required=True, help="Output directory (dist/portable)")
    ap_port.add_argument("--version", required=True, help="Artifact/product version (x.y.z)")
    ap_port.add_argument("--reproducible", action="store_true", help="Enforce strict reproducible mode (requires SOURCE_DATE_EPOCH).")
    ap_port.set_defaults(func=package_portable)

    ap_win = sub.add_parser("windows", help="Build Windows MSI (and optional bootstrapper EXE) from an assembled artifact_root/.")
    ap_win.add_argument("--artifact", required=True, help="Input artifact_root/ directory")
    ap_win.add_argument("--out", required=True, help="Output directory (dist/windows)")
    ap_win.add_argument("--version", required=True, help="Artifact/product version (x.y.z)")
    ap_win.add_argument("--bootstrapper", action="store_true", help="Also build a Burn bootstrapper EXE.")
    ap_win.add_argument("--reproducible", action="store_true", help="Enforce strict reproducible mode (requires SOURCE_DATE_EPOCH).")
    ap_win.set_defaults(func=package_windows)

    ap_steam = sub.add_parser("steam", help="Stage SteamPipe depot(s) containing the canonical artifact layout.")
    ap_steam.add_argument("--artifact", required=True, help="Input artifact_root/ directory")
    ap_steam.add_argument("--out", required=True, help="Output directory (dist/steam)")
    ap_steam.add_argument("--version", required=True, help="Artifact/product version (x.y.z)")
    ap_steam.add_argument("--appid", type=int, default=0, help="Steam AppID (default: 0 placeholder)")
    ap_steam.add_argument("--depotid", type=int, default=0, help="Steam DepotID (default: 0 placeholder)")
    ap_steam.add_argument("--reproducible", action="store_true", help="Enforce strict reproducible mode (requires SOURCE_DATE_EPOCH).")
    ap_steam.set_defaults(func=package_steam)

    ap_macos = sub.add_parser("macos", help="Build macOS PKG + DMG from an assembled artifact_root/.")
    ap_macos.add_argument("--artifact", required=True, help="Input artifact_root/ directory")
    ap_macos.add_argument("--out", required=True, help="Output directory (dist/macos)")
    ap_macos.add_argument("--version", required=True, help="Artifact/product version (x.y.z)")
    ap_macos.add_argument("--identifier", default="com.dominium.game", help="PKG identifier (default: com.dominium.game)")
    ap_macos.add_argument("--reproducible", action="store_true", help="Enforce strict reproducible mode (requires SOURCE_DATE_EPOCH).")
    ap_macos.set_defaults(func=package_macos)

    ap_linux = sub.add_parser("linux", help="Build Linux tarball (+ optional deb/rpm) from an assembled artifact_root/.")
    ap_linux.add_argument("--artifact", required=True, help="Input artifact_root/ directory")
    ap_linux.add_argument("--out", required=True, help="Output directory (dist/linux)")
    ap_linux.add_argument("--version", required=True, help="Artifact/product version (x.y.z)")
    ap_linux.add_argument("--build-deb", action="store_true", help="Build .deb (requires dpkg-deb).")
    ap_linux.add_argument("--build-rpm", action="store_true", help="Build .rpm (requires rpmbuild).")
    ap_linux.add_argument("--maintainer", default="Dominium <support@dominium.invalid>", help="deb control Maintainer field")
    ap_linux.add_argument("--depends", default="", help="deb control Depends field")
    ap_linux.add_argument("--release", default="1", help="rpm Release (default: 1)")
    ap_linux.add_argument("--requires", default="", help="rpm Requires field")
    ap_linux.add_argument("--reproducible", action="store_true", help="Enforce strict reproducible mode (requires SOURCE_DATE_EPOCH).")
    ap_linux.set_defaults(func=package_linux)

    args = ap.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
