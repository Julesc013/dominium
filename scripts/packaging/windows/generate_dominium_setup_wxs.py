#!/usr/bin/env python3
from __future__ import print_function

import argparse
import hashlib
import os
import sys


def _norm_rel(path):
    path = path.replace("/", "\\")
    while path.startswith(".\\"):
        path = path[2:]
    while path.startswith("\\"):
        path = path[1:]
    return path


def _iter_files(root_dir):
    root_dir = os.path.abspath(root_dir)
    rel_files = []
    rel_dirs = set()
    for cur_root, cur_dirs, cur_files in os.walk(root_dir):
        cur_dirs.sort()
        cur_files.sort()
        rel_root = os.path.relpath(cur_root, root_dir)
        rel_root = "" if rel_root == "." else _norm_rel(rel_root)
        for d in cur_dirs:
            rel_dirs.add(_norm_rel(os.path.join(rel_root, d)))
        for f in cur_files:
            rel = _norm_rel(os.path.join(rel_root, f))
            rel_files.append(rel)
    rel_files = sorted(set(rel_files))
    rel_dirs = sorted(rel_dirs)
    return rel_dirs, rel_files


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


class DirNode(object):
    __slots__ = ("name", "rel", "id", "children", "files")

    def __init__(self, name, rel):
        self.name = name
        self.rel = rel
        self.id = _wix_id("DIR", rel if rel else "ROOT")
        self.children = {}
        self.files = []


def _build_tree(rel_dirs, rel_files):
    root = DirNode("INSTALLDIR", "")

    def ensure_dir(rel):
        if not rel:
            return root
        parts = [p for p in rel.split("\\") if p]
        cur = root
        cur_rel = ""
        for p in parts:
            cur_rel = p if not cur_rel else (cur_rel + "\\" + p)
            if p not in cur.children:
                cur.children[p] = DirNode(p, cur_rel)
            cur = cur.children[p]
        return cur

    for d in rel_dirs:
        ensure_dir(d)

    for f in rel_files:
        drel = os.path.dirname(f)
        node = ensure_dir(drel)
        node.files.append(f)

    return root


def _emit_dir(out, node, indent, all_component_ids):
    ind = " " * indent
    for name in sorted(node.children.keys()):
        child = node.children[name]
        out.write('%s<Directory Id="%s" Name="%s">\n' % (
            ind, _escape_attr(child.id), _escape_attr(child.name)
        ))
        _emit_dir(out, child, indent + 2, all_component_ids)
        out.write('%s</Directory>\n' % ind)

    for rel_f in sorted(node.files):
        comp_id = _wix_id("CMP", rel_f)
        file_id = _wix_id("FIL", rel_f)
        guid = _wix_guid_for_path(rel_f)
        all_component_ids.append(comp_id)

        src = '$(var.ArtifactDir)\\%s' % rel_f
        out.write('%s<Component Id="%s" Guid="%s">\n' % (ind, _escape_attr(comp_id), _escape_attr(guid)))
        out.write('%s  <File Id="%s" Source="%s" KeyPath="yes" />\n' % (
            ind, _escape_attr(file_id), _escape_attr(src)
        ))
        out.write('%s</Component>\n' % ind)


def main(argv):
    ap = argparse.ArgumentParser(description="Generate a WiX .wxs for staging an artifact_root/ tree and invoking dominium-setup.")
    ap.add_argument("--artifact-dir", required=True, help="Assembled artifact_root/ directory (must match -dArtifactDir)")
    ap.add_argument("--out", required=True, help="Output .wxs path")
    ap.add_argument("--product-version", required=True, help="MSI ProductVersion (numeric, e.g. 0.1.0)")
    ap.add_argument("--manufacturer", required=True, help="Manufacturer string")
    ap.add_argument("--product-code", required=True, help="Deterministic ProductCode GUID (with braces)")
    ap.add_argument("--upgrade-code", required=True, help="UpgradeCode GUID (with braces)")
    ap.add_argument("--package-code", required=True, help="Deterministic PackageCode GUID (with braces)")
    ap.add_argument("--license-file", required=True, help="License RTF path")
    args = ap.parse_args(argv)

    artifact_dir = os.path.abspath(args.artifact_dir)
    out_path = os.path.abspath(args.out)

    if not os.path.isdir(artifact_dir):
        raise SystemExit("artifact-dir not found: %s" % artifact_dir)

    rel_dirs, rel_files = _iter_files(artifact_dir)
    tree = _build_tree(rel_dirs, rel_files)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    component_ids = []
    with open(out_path, "w", encoding="utf-8", newline="\n") as out:
        out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        out.write('<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">\n')
        out.write('  <Product\n')
        out.write('    Id="%s"\n' % _escape_attr(args.product_code))
        out.write('    Name="Dominium Setup"\n')
        out.write('    Language="1033"\n')
        out.write('    Version="%s"\n' % _escape_attr(args.product_version))
        out.write('    Manufacturer="%s"\n' % _escape_attr(args.manufacturer))
        out.write('    UpgradeCode="%s">\n' % _escape_attr(args.upgrade_code))
        out.write('\n')
        out.write('    <Package InstallerVersion="500" Compressed="yes" InstallScope="perMachine" Id="%s" />\n' % _escape_attr(args.package_code))
        out.write('    <MajorUpgrade DowngradeErrorMessage="A newer version of Dominium is already installed." />\n')
        out.write('    <MediaTemplate EmbedCab="yes" CompressionLevel="high" />\n')
        out.write('\n')
        out.write('    <Property Id="ARPCONTACT" Value="%s" />\n' % _escape_attr(args.manufacturer))
        out.write('    <Property Id="ARPNOMODIFY" Value="yes" />\n')
        out.write('    <Property Id="ARPNOREPAIR" Value="no" />\n')
        out.write('    <Property Id="WIXUI_INSTALLDIR" Value="INSTALLDIR" />\n')
        out.write('    <WixVariable Id="WixUILicenseRtf" Value="%s" />\n' % _escape_attr(args.license_file))
        out.write('\n')
        out.write('    <!-- Setup Core parameter surface (UI/CLI can set these MSI properties). -->\n')
        out.write('    <Property Id="DSU_SCOPE" Secure="yes" Value="user" />\n')
        out.write('    <Property Id="DSU_DETERMINISTIC" Secure="yes" Value="1" />\n')
        out.write('\n')
        out.write('    <!-- Per-user/system selection (standard MSI semantics). -->\n')
        out.write('    <Property Id="ALLUSERS" Secure="yes" Value="1" />\n')
        out.write('    <Property Id="MSIINSTALLPERUSER" Secure="yes" />\n')
        out.write('    <SetProperty Id="ALLUSERS" Value="2" After="LaunchConditions">NOT Privileged AND NOT ALLUSERS</SetProperty>\n')
        out.write('    <SetProperty Id="MSIINSTALLPERUSER" Value="1" After="CostFinalize">NOT Privileged OR ALLUSERS=2</SetProperty>\n')
        out.write('    <SetProperty Id="INSTALLDIR" Value="[LocalAppDataFolder]Dominium\\artifact_root" After="CostFinalize">NOT Privileged OR ALLUSERS=2 OR MSIINSTALLPERUSER=1</SetProperty>\n')
        out.write('\n')
        out.write('    <Directory Id="TARGETDIR" Name="SourceDir">\n')
        out.write('      <Directory Id="ProgramMenuFolder">\n')
        out.write('        <Directory Id="DominiumProgramMenu" Name="Dominium" />\n')
        out.write('      </Directory>\n')
        out.write('      <Directory Id="DesktopFolder" />\n')
        out.write('      <Directory Id="ProgramFilesFolder">\n')
        out.write('        <Directory Id="INSTALLDIR" Name="Dominium">\n')
        _emit_dir(out, tree, 10, component_ids)
        out.write('        </Directory>\n')
        out.write('      </Directory>\n')
        out.write('    </Directory>\n')
        out.write('\n')
        out.write('    <ComponentGroup Id="DominiumArtifactFiles">\n')
        for cid in component_ids:
            out.write('      <ComponentRef Id="%s" />\n' % _escape_attr(cid))
        out.write('    </ComponentGroup>\n')
        out.write('\n')
        out.write('    <Feature Id="DominiumArtifact" Title="Dominium (artifact)" Level="1" Absent="disallow">\n')
        out.write('      <ComponentGroupRef Id="DominiumArtifactFiles" />\n')
        out.write('    </Feature>\n')
        out.write('\n')
        out.write('    <!-- Custom actions: only invoke Setup Core CLI. -->\n')
        out.write('    <CustomAction Id="DSU_SetInvocation"\n')
        out.write('                  Property="DSU_RunInvocation"\n')
        out.write('                  Value="&quot;[INSTALLDIR]setup\\dominium-setup.exe&quot; --deterministic [DSU_DETERMINISTIC] export-invocation --manifest &quot;[INSTALLDIR]setup\\manifests\\product.dsumanifest&quot; --op install --scope [DSU_SCOPE] --ui-mode gui --frontend-id msi --out &quot;[TempFolder]dominium.dsuinv&quot;" />\n')
        out.write('    <CustomAction Id="DSU_RunInvocation"\n')
        out.write('                  BinaryKey="WixCA"\n')
        out.write('                  DllEntry="CAQuietExec"\n')
        out.write('                  Execute="deferred"\n')
        out.write('                  Return="check"\n')
        out.write('                  Impersonate="no" />\n')
        out.write('\n')
        out.write('    <CustomAction Id="DSU_SetPlan"\n')
        out.write('                  Property="DSU_RunPlan"\n')
        out.write('                  Value="&quot;[INSTALLDIR]setup\\dominium-setup.exe&quot; --deterministic [DSU_DETERMINISTIC] plan --manifest &quot;[INSTALLDIR]setup\\manifests\\product.dsumanifest&quot; --invocation &quot;[TempFolder]dominium.dsuinv&quot; --out &quot;[TempFolder]dominium.dsuplan&quot;" />\n')
        out.write('    <CustomAction Id="DSU_RunPlan"\n')
        out.write('                  BinaryKey="WixCA"\n')
        out.write('                  DllEntry="CAQuietExec"\n')
        out.write('                  Execute="deferred"\n')
        out.write('                  Return="check"\n')
        out.write('                  Impersonate="no" />\n')
        out.write('\n')
        out.write('    <CustomAction Id="DSU_SetApply"\n')
        out.write('                  Property="DSU_RunApply"\n')
        out.write('                  Value="&quot;[INSTALLDIR]setup\\dominium-setup.exe&quot; --deterministic [DSU_DETERMINISTIC] apply --plan &quot;[TempFolder]dominium.dsuplan&quot;" />\n')
        out.write('    <CustomAction Id="DSU_RunApply"\n')
        out.write('                  BinaryKey="WixCA"\n')
        out.write('                  DllEntry="CAQuietExec"\n')
        out.write('                  Execute="deferred"\n')
        out.write('                  Return="check"\n')
        out.write('                  Impersonate="no" />\n')
        out.write('\n')
        out.write('    <InstallExecuteSequence>\n')
        out.write('      <Custom Action="DSU_SetInvocation" After="InstallFiles">NOT Installed</Custom>\n')
        out.write('      <Custom Action="DSU_RunInvocation" After="DSU_SetInvocation">NOT Installed</Custom>\n')
        out.write('      <Custom Action="DSU_SetPlan" After="DSU_RunInvocation">NOT Installed</Custom>\n')
        out.write('      <Custom Action="DSU_RunPlan" After="DSU_SetPlan">NOT Installed</Custom>\n')
        out.write('      <Custom Action="DSU_SetApply" After="DSU_RunPlan">NOT Installed</Custom>\n')
        out.write('      <Custom Action="DSU_RunApply" After="DSU_SetApply">NOT Installed</Custom>\n')
        out.write('    </InstallExecuteSequence>\n')
        out.write('\n')
        out.write('    <UIRef Id="WixUI_InstallDir" />\n')
        out.write('  </Product>\n')
        out.write('</Wix>\n')

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
