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


def _iter_files(stage_dir):
    stage_dir = os.path.abspath(stage_dir)
    rel_files = []
    rel_dirs = set()
    for cur_root, cur_dirs, cur_files in os.walk(stage_dir):
        cur_dirs.sort()
        cur_files.sort()
        rel_root = os.path.relpath(cur_root, stage_dir)
        rel_root = "" if rel_root == "." else _norm_rel(rel_root)
        for d in cur_dirs:
            rel_dirs.add(_norm_rel(os.path.join(rel_root, d)))
        for f in cur_files:
            rel = _norm_rel(os.path.join(rel_root, f))
            # Exclude internal staging stamp.
            if rel.lower() in (".stage_stamp", ".stage_stamp".replace("/", "\\")):
                continue
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
    # The root node is emitted elsewhere as INSTALLDIR.
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

        src = '$(var.DistDir)\\%s' % rel_f
        out.write('%s<Component Id="%s" Guid="%s">\n' % (ind, _escape_attr(comp_id), _escape_attr(guid)))
        out.write('%s  <File Id="%s" Source="%s" KeyPath="yes" />\n' % (
            ind, _escape_attr(file_id), _escape_attr(src)
        ))
        out.write('%s</Component>\n' % ind)


def main(argv):
    ap = argparse.ArgumentParser(description="Generate a WiX .wxs for installing a staged Dominium directory tree.")
    ap.add_argument("--stage-dir", required=True, help="Staging directory root (must match -dDistDir)")
    ap.add_argument("--out", required=True, help="Output .wxs path")
    ap.add_argument("--product-version", required=True, help="Product version (MSI numeric, e.g. 0.1.0)")
    ap.add_argument("--manufacturer", required=True, help="Manufacturer string")
    ap.add_argument("--product-code", required=True, help="Deterministic ProductCode GUID (with braces)")
    ap.add_argument("--upgrade-code", required=True, help="UpgradeCode GUID (with braces)")
    ap.add_argument("--license-file", required=True, help="License RTF path")
    args = ap.parse_args(argv)

    stage_dir = os.path.abspath(args.stage_dir)
    out_path = os.path.abspath(args.out)

    if not os.path.isdir(stage_dir):
        raise SystemExit("stage-dir not found: %s" % stage_dir)

    rel_dirs, rel_files = _iter_files(stage_dir)
    tree = _build_tree(rel_dirs, rel_files)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    component_ids = []
    with open(out_path, "w", encoding="utf-8", newline="\n") as out:
        out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        out.write('<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">\n')
        out.write('  <Product\n')
        out.write('    Id="%s"\n' % _escape_attr(args.product_code))
        out.write('    Name="Dominium"\n')
        out.write('    Language="1033"\n')
        out.write('    Version="%s"\n' % _escape_attr(args.product_version))
        out.write('    Manufacturer="%s"\n' % _escape_attr(args.manufacturer))
        out.write('    UpgradeCode="%s">\n' % _escape_attr(args.upgrade_code))
        out.write('\n')
        out.write('    <Package InstallerVersion="500" Compressed="yes" InstallScope="perUser" />\n')
        out.write('    <MajorUpgrade DowngradeErrorMessage="A newer version of Dominium is already installed." />\n')
        out.write('    <MediaTemplate EmbedCab="yes" CompressionLevel="high" />\n')
        out.write('\n')
        out.write('    <Property Id="ARPCONTACT" Value="%s" />\n' % _escape_attr(args.manufacturer))
        out.write('    <Property Id="ARPNOMODIFY" Value="yes" />\n')
        out.write('    <Property Id="ARPNOREPAIR" Value="no" />\n')
        out.write('    <Property Id="WIXUI_INSTALLDIR" Value="INSTALLDIR" />\n')
        out.write('    <WixVariable Id="WixUILicenseRtf" Value="%s" />\n' % _escape_attr(args.license_file))
        out.write('\n')
        out.write('    <Directory Id="TARGETDIR" Name="SourceDir">\n')
        out.write('      <Directory Id="ProgramMenuFolder">\n')
        out.write('        <Directory Id="DominiumProgramMenu" Name="Dominium" />\n')
        out.write('      </Directory>\n')
        out.write('      <Directory Id="DesktopFolder" />\n')
        out.write('      <Directory Id="LocalAppDataFolder">\n')
        out.write('        <Directory Id="DominiumRoot" Name="dominium">\n')
        out.write('          <Directory Id="INSTALLDIR" Name="data">\n')
        _emit_dir(out, tree, 12, component_ids)
        out.write('          </Directory>\n')
        out.write('        </Directory>\n')
        out.write('      </Directory>\n')
        out.write('    </Directory>\n')
        out.write('\n')
        out.write('    <ComponentGroup Id="DominiumFiles">\n')
        for cid in component_ids:
            out.write('      <ComponentRef Id="%s" />\n' % _escape_attr(cid))
        out.write('    </ComponentGroup>\n')
        out.write('\n')
        out.write('    <Component Id="cmpShortcuts" Guid="%s" Directory="INSTALLDIR">\n' % _escape_attr(_wix_guid_for_path("shortcuts")))
        out.write('      <Shortcut Id="ShortcutStartMenu"\n')
        out.write('                Directory="DominiumProgramMenu"\n')
        out.write('                Name="Dominium"\n')
        out.write('                Target="[INSTALLDIR]bin\\dominium-launcher.exe"\n')
        out.write('                WorkingDirectory="INSTALLDIR" />\n')
        out.write('      <Shortcut Id="ShortcutDesktop"\n')
        out.write('                Directory="DesktopFolder"\n')
        out.write('                Name="Dominium"\n')
        out.write('                Target="[INSTALLDIR]bin\\dominium-launcher.exe"\n')
        out.write('                WorkingDirectory="INSTALLDIR" />\n')
        out.write('      <RemoveFolder Id="RemoveDominiumProgramMenu" Directory="DominiumProgramMenu" On="uninstall" />\n')
        out.write('      <RegistryValue Root="HKCU" Key="Software\\Dominium\\Installer" Name="Shortcuts" Type="integer" Value="1" KeyPath="yes" />\n')
        out.write('    </Component>\n')
        out.write('\n')
        out.write('    <Feature Id="MainApplication" Title="Dominium" Level="1" Absent="disallow">\n')
        out.write('      <ComponentGroupRef Id="DominiumFiles" />\n')
        out.write('      <ComponentRef Id="cmpShortcuts" />\n')
        out.write('    </Feature>\n')
        out.write('\n')
        out.write('    <UIRef Id="WixUI_InstallDir" />\n')
        out.write('  </Product>\n')
        out.write('</Wix>\n')

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

