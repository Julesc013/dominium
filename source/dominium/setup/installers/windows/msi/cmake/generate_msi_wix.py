#!/usr/bin/env python3
from __future__ import print_function

import argparse
import hashlib
import json
import os
import re
import sys


def _norm_rel(path):
    path = path.replace("/", "\\")
    while path.startswith(".\\"):
        path = path[2:]
    while path.startswith("\\"):
        path = path[1:]
    return path


def _md5_hex(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _wix_id(prefix, s):
    h = _md5_hex(s).upper()
    return "%s_%s" % (prefix, h[:16])


def _wix_guid_for_path(rel_path):
    h = _md5_hex(rel_path)
    return "{%s-%s-%s-%s-%s}" % (h[0:8], h[8:12], h[12:16], h[16:20], h[20:32])


def _escape_attr(s):
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace("\"", "&quot;"))


def _is_wix_id(s):
    if not s:
        return False
    return re.match(r"^[A-Za-z_][A-Za-z0-9_.]*$", s) is not None


def _load_manifest_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _iter_resource_files(artifact_dir):
    keep = []
    for cur_root, _dirs, files in os.walk(artifact_dir):
        files = sorted(files)
        rel_root = os.path.relpath(cur_root, artifact_dir)
        rel_root = "" if rel_root == "." else _norm_rel(rel_root)
        for fn in files:
            rel = _norm_rel(os.path.join(rel_root, fn))
            keep.append(rel)
    return keep


def _dir_id_for_rel(rel_path):
    parts = rel_path.replace("\\", "/").split("/")
    if not parts:
        return None
    if parts[0] == "setup":
        if len(parts) >= 2 and parts[1] == "manifests":
            return "DSU_MANIFESTS_DIR"
        if len(parts) >= 2 and parts[1] == "policies":
            return "DSU_POLICIES_DIR"
        return "DSU_SETUP_DIR"
    if parts[0] == "payloads":
        if len(parts) != 2:
            return None
        return "DSU_PAYLOADS_DIR"
    return None


def _emit_components(artifact_dir, out_path):
    rel_files = _iter_resource_files(artifact_dir)
    components = []
    for rel in rel_files:
        dir_id = _dir_id_for_rel(rel)
        if not dir_id:
            continue
        components.append((rel, dir_id))

    with open(out_path, "w", encoding="utf-8", newline="\n") as out:
        out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        out.write('<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">\n')
        out.write('  <Fragment>\n')
        out.write('    <ComponentGroup Id="DominiumInstallerResources">\n')
        for rel, _dir_id in components:
            out.write('      <ComponentRef Id="%s" />\n' % _escape_attr(_wix_id("CMP", rel)))
        out.write('    </ComponentGroup>\n')
        out.write('  </Fragment>\n')
        out.write('  <Fragment>\n')
        for rel, dir_id in components:
            comp_id = _wix_id("CMP", rel)
            file_id = _wix_id("FIL", rel)
            guid = _wix_guid_for_path(rel)
            src = '$(var.ArtifactDir)\\%s' % rel
            out.write('    <Component Id="%s" Guid="%s" Directory="%s">\n' %
                      (_escape_attr(comp_id), _escape_attr(guid), _escape_attr(dir_id)))
            out.write('      <File Id="%s" Source="%s" KeyPath="yes" />\n' %
                      (_escape_attr(file_id), _escape_attr(src)))
            out.write('    </Component>\n')
        out.write('  </Fragment>\n')
        out.write('</Wix>\n')


def _emit_features(manifest_json, out_path):
    comps = manifest_json.get("components", [])
    if not comps:
        raise SystemExit("manifest has no components")

    resource_host = None
    for comp in comps:
        flags = int(comp.get("flags", 0))
        if (flags & 0x1) == 0:
            resource_host = comp.get("component_id")
            break
    if not resource_host:
        resource_host = comps[0].get("component_id")

    with open(out_path, "w", encoding="utf-8", newline="\n") as out:
        out.write('<!-- Generated: MSI features mapped 1:1 to manifest components. -->\n')
        for comp in comps:
            cid = comp.get("component_id", "")
            flags = int(comp.get("flags", 0))
            optional = (flags & 0x1) != 0
            default_selected = (flags & 0x2) != 0
            hidden = (flags & 0x4) != 0

            if not _is_wix_id(cid):
                raise SystemExit("component_id not MSI-safe: %s" % cid)

            level = "1" if (default_selected or not optional) else "200"
            attrs = []
            if not optional:
                attrs.append('Absent="disallow"')
            if hidden:
                attrs.append('Display="hidden"')
            attr_text = (" " + " ".join(attrs)) if attrs else ""

            out.write('  <Feature Id="%s" Title="%s" Level="%s"%s>\n' %
                      (_escape_attr(cid), _escape_attr(cid), level, attr_text))
            if cid == resource_host:
                out.write('    <ComponentGroupRef Id="DominiumInstallerResources" />\n')
            out.write('  </Feature>\n')


def main(argv):
    ap = argparse.ArgumentParser(description="Generate WiX fragments for Dominium MSI.")
    ap.add_argument("--artifact-dir", required=True, help="artifact_root/ directory")
    ap.add_argument("--manifest-json", required=True, help="Manifest JSON dump (dominium-setup manifest dump)")
    ap.add_argument("--features-out", required=True, help="Output .wxi file for Feature entries")
    ap.add_argument("--components-out", required=True, help="Output .wxs file for ComponentGroup")
    args = ap.parse_args(argv)

    artifact_dir = os.path.abspath(args.artifact_dir)
    if not os.path.isdir(artifact_dir):
        raise SystemExit("artifact-dir missing: %s" % artifact_dir)

    manifest_json = _load_manifest_json(args.manifest_json)
    _emit_features(manifest_json, args.features_out)
    _emit_components(artifact_dir, args.components_out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
