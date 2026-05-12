#!/usr/bin/env python3
from __future__ import print_function

import hashlib
import json
import os
import re
import struct


DSU_MAGIC = b"DSUM"
DSU_FORMAT_VERSION = 2
DSU_ENDIAN_MARKER_LE = 0xFFFE
DSU_HEADER_SIZE = 20


# TLV type ids (locked; see docs/setup/MANIFEST_SCHEMA.md)
TLV_MANIFEST_ROOT = 0x0001
TLV_ROOT_VERSION = 0x0002
TLV_PRODUCT_ID = 0x0010
TLV_PRODUCT_VERSION = 0x0011
TLV_BUILD_CHANNEL = 0x0012
TLV_PLATFORM_TARGET = 0x0020

TLV_DEFAULT_INSTALL_ROOT = 0x0030
TLV_INSTALL_ROOT_VERSION = 0x0031
TLV_INSTALL_SCOPE = 0x0032
TLV_INSTALL_PLATFORM = 0x0033
TLV_INSTALL_PATH = 0x0034

TLV_COMPONENT = 0x0040
TLV_COMPONENT_VERSION = 0x0041
TLV_COMPONENT_ID = 0x0042
TLV_COMPONENT_VERSTR = 0x0043
TLV_COMPONENT_KIND = 0x0044
TLV_COMPONENT_FLAGS = 0x0045

TLV_DEPENDENCY = 0x0046
TLV_DEP_VERSION = 0x0047
TLV_DEP_COMPONENT_ID = 0x0048
TLV_DEP_CONSTRAINT_KIND = 0x0049
TLV_DEP_CONSTRAINT_VERSION = 0x004A

TLV_CONFLICT = 0x004B

TLV_PAYLOAD = 0x004C
TLV_PAYLOAD_VERSION = 0x004D
TLV_PAYLOAD_KIND = 0x004E
TLV_PAYLOAD_PATH = 0x004F
TLV_PAYLOAD_SHA256 = 0x0050
TLV_PAYLOAD_SIZE = 0x0051

TLV_ACTION = 0x0052
TLV_ACTION_VERSION = 0x0053
TLV_ACTION_KIND = 0x0054
TLV_ACTION_APP_ID = 0x0055
TLV_ACTION_DISPLAY_NAME = 0x0056
TLV_ACTION_EXEC_RELPATH = 0x0057
TLV_ACTION_ARGUMENTS = 0x0058
TLV_ACTION_ICON_RELPATH = 0x0059
TLV_ACTION_EXTENSION = 0x005A
TLV_ACTION_PROTOCOL = 0x005B
TLV_ACTION_MARKER_RELPATH = 0x005C
TLV_ACTION_CAPABILITY_ID = 0x005D
TLV_ACTION_CAPABILITY_VALUE = 0x005E
TLV_ACTION_PUBLISHER = 0x005F

TLV_UNINSTALL_POLICY = 0x0060
TLV_POLICY_VERSION = 0x0061
TLV_POLICY_REMOVE_OWNED = 0x0062
TLV_POLICY_PRESERVE_USER_DATA = 0x0063
TLV_POLICY_PRESERVE_CACHE = 0x0064


_ID_RE = re.compile(r"^[a-z0-9._-]+$")


def _u8(v):
    return struct.pack("<B", int(v) & 0xFF)


def _u16(v):
    return struct.pack("<H", int(v) & 0xFFFF)


def _u32(v):
    return struct.pack("<I", int(v) & 0xFFFFFFFF)


def _u64(v):
    return struct.pack("<Q", int(v) & 0xFFFFFFFFFFFFFFFF)


def _tlv(t, payload):
    if payload is None:
        payload = b""
    return _u16(t) + _u32(len(payload)) + payload


def _tlv_u8(t, v):
    return _tlv(t, _u8(v))


def _tlv_u32(t, v):
    return _tlv(t, _u32(v))


def _tlv_u64(t, v):
    return _tlv(t, _u64(v))


def _tlv_str(t, s):
    if s is None:
        s = ""
    if not isinstance(s, str):
        raise TypeError("expected string for tlv 0x%04x" % t)
    if "\x00" in s:
        raise ValueError("embedded NUL not allowed for tlv 0x%04x" % t)
    return _tlv(t, s.encode("utf-8"))


def _norm_id(s):
    s = (s or "").strip().lower()
    if not s:
        return ""
    if not _ID_RE.match(s):
        raise ValueError("invalid id: %r" % s)
    return s


def _norm_path(s):
    s = (s or "").strip()
    s = s.replace("\\", "/")
    while s.startswith("./"):
        s = s[2:]
    while s.startswith("/"):
        s = s[1:]
    return s


def _parse_sha256_hex(s):
    s = (s or "").strip().lower()
    if s == "auto" or s == "":
        raise ValueError("sha256 must be concrete hex, got %r" % s)
    if s.startswith("0x"):
        s = s[2:]
    if len(s) != 64:
        raise ValueError("sha256 must be 64 hex chars, got %r" % s)
    try:
        b = bytes.fromhex(s)
    except Exception:
        raise ValueError("invalid sha256 hex: %r" % s)
    if len(b) != 32:
        raise ValueError("invalid sha256 length for %r" % s)
    return b


def _install_scope_u8(scope_name):
    scope_name = (scope_name or "").strip().lower()
    if scope_name == "portable":
        return 0
    if scope_name == "user":
        return 1
    if scope_name == "system":
        return 2
    raise ValueError("unknown install scope: %r" % scope_name)


def _component_kind_u8(kind_name):
    kind_name = (kind_name or "").strip().lower()
    if kind_name == "launcher":
        return 0
    if kind_name == "runtime":
        return 1
    if kind_name == "tools":
        return 2
    if kind_name == "pack":
        return 3
    if kind_name == "driver":
        return 4
    if kind_name == "other":
        return 5
    raise ValueError("unknown component kind: %r" % kind_name)


def _payload_kind_u8(kind_name):
    kind_name = (kind_name or "").strip().lower()
    if kind_name == "fileset":
        return 0
    if kind_name == "archive":
        return 1
    if kind_name == "blob":
        return 2
    raise ValueError("unknown payload kind: %r" % kind_name)


def _dep_constraint_kind_u8(kind_name):
    kind_name = (kind_name or "").strip().lower()
    if kind_name == "any":
        return 0
    if kind_name == "exact":
        return 1
    if kind_name in ("at_least", "at-least"):
        return 2
    raise ValueError("unknown dependency constraint kind: %r" % kind_name)


def _action_kind_u8(kind_name):
    kind_name = (kind_name or "").strip().upper()
    if kind_name == "REGISTER_APP_ENTRY":
        return 0
    if kind_name == "REGISTER_FILE_ASSOC":
        return 1
    if kind_name == "REGISTER_URL_HANDLER":
        return 2
    if kind_name == "REGISTER_UNINSTALL_ENTRY":
        return 3
    if kind_name == "WRITE_FIRST_RUN_MARKER":
        return 4
    if kind_name == "DECLARE_CAPABILITY":
        return 5
    raise ValueError("unknown action kind: %r" % kind_name)


def _canonicalize_manifest_json(m):
    m = dict(m or {})

    m["product_id"] = _norm_id(m.get("product_id", ""))

    def _canon_platform_list(items):
        out = []
        for it in items or []:
            s = (it or "").strip().lower()
            if s:
                out.append(s)
        return sorted(set(out))

    m["platform_targets"] = _canon_platform_list(m.get("platform_targets", []))

    roots = []
    for r in m.get("default_install_roots", []) or []:
        rr = dict(r or {})
        rr["scope"] = (rr.get("scope") or "").strip().lower()
        rr["platform"] = (rr.get("platform") or "").strip().lower()
        rr["path"] = (rr.get("path") or "").strip()
        roots.append(rr)
    roots.sort(key=lambda x: (x.get("platform", ""), x.get("scope", ""), x.get("path", "")))
    m["default_install_roots"] = roots

    comps = []
    for c in m.get("components", []) or []:
        cc = dict(c or {})
        cc["component_id"] = _norm_id(cc.get("component_id", ""))
        cc["component_kind"] = (cc.get("component_kind") or "").strip().lower()
        cc["component_version"] = (cc.get("component_version") or "")
        cc["flags"] = int(cc.get("flags") or 0)

        deps = []
        for d in cc.get("dependencies", []) or []:
            dd = dict(d or {})
            dd["id"] = _norm_id(dd.get("id", ""))
            dd["constraint"] = (dd.get("constraint") or "any").strip().lower()
            dd["version"] = (dd.get("version") or "")
            deps.append(dd)
        deps.sort(key=lambda x: (x.get("id", ""), x.get("constraint", ""), x.get("version", "")))
        cc["dependencies"] = deps

        conflicts = []
        for x in cc.get("conflicts", []) or []:
            x = _norm_id(x)
            if x:
                conflicts.append(x)
        cc["conflicts"] = sorted(set(conflicts))

        payloads = []
        for p in cc.get("payloads", []) or []:
            pp = dict(p or {})
            pp["kind"] = (pp.get("kind") or "").strip().lower()
            pp["path"] = _norm_path(pp.get("path") or "")
            if "sha256" in pp and isinstance(pp["sha256"], str):
                pp["sha256"] = pp["sha256"].strip().lower()
            payloads.append(pp)
        payloads.sort(key=lambda x: (x.get("path", ""), x.get("kind", ""), x.get("sha256", "")))
        cc["payloads"] = payloads

        actions = []
        for a in cc.get("actions", []) or []:
            aa = dict(a or {})
            aa["kind"] = (aa.get("kind") or "").strip().upper()
            if "app_id" in aa:
                aa["app_id"] = _norm_id(aa.get("app_id") or "")
            if "capability_id" in aa:
                aa["capability_id"] = _norm_id(aa.get("capability_id") or "")
            if "exec_relpath" in aa:
                aa["exec_relpath"] = _norm_path(aa.get("exec_relpath") or "")
            if "icon_relpath" in aa:
                aa["icon_relpath"] = _norm_path(aa.get("icon_relpath") or "")
            if "marker_relpath" in aa:
                aa["marker_relpath"] = _norm_path(aa.get("marker_relpath") or "")
            if "extension" in aa:
                aa["extension"] = (aa.get("extension") or "")
            if "protocol" in aa:
                aa["protocol"] = (aa.get("protocol") or "")
            actions.append(aa)
        actions.sort(key=lambda x: (
            x.get("kind", ""),
            x.get("app_id", ""),
            x.get("extension", ""),
            x.get("protocol", ""),
            x.get("exec_relpath", ""),
            x.get("marker_relpath", ""),
            x.get("display_name", ""),
        ))
        cc["actions"] = actions

        comps.append(cc)
    comps.sort(key=lambda x: x.get("component_id", ""))
    m["components"] = comps

    if "uninstall_policy" in m and m["uninstall_policy"] is not None:
        up = dict(m.get("uninstall_policy") or {})
        up["remove_owned_files"] = int(up.get("remove_owned_files") or 0)
        up["preserve_user_data"] = int(up.get("preserve_user_data") or 0)
        up["preserve_cache"] = int(up.get("preserve_cache") or 0)
        m["uninstall_policy"] = up

    return m


def compile_dsumanifest_from_json(manifest_json_obj):
    m = _canonicalize_manifest_json(manifest_json_obj)

    root_items = []
    root_items.append(_tlv_u32(TLV_ROOT_VERSION, 1))
    root_items.append(_tlv_str(TLV_PRODUCT_ID, m.get("product_id", "")))
    root_items.append(_tlv_str(TLV_PRODUCT_VERSION, m.get("product_version", "")))
    root_items.append(_tlv_str(TLV_BUILD_CHANNEL, m.get("build_channel", "")))

    for pt in m.get("platform_targets", []) or []:
        root_items.append(_tlv_str(TLV_PLATFORM_TARGET, (pt or "").strip().lower()))

    for r in m.get("default_install_roots", []) or []:
        items = []
        items.append(_tlv_u32(TLV_INSTALL_ROOT_VERSION, 1))
        items.append(_tlv_u8(TLV_INSTALL_SCOPE, _install_scope_u8(r.get("scope"))))
        items.append(_tlv_str(TLV_INSTALL_PLATFORM, (r.get("platform") or "").strip().lower()))
        items.append(_tlv_str(TLV_INSTALL_PATH, (r.get("path") or "").strip()))
        root_items.append(_tlv(TLV_DEFAULT_INSTALL_ROOT, b"".join(items)))

    for c in m.get("components", []) or []:
        items = []
        items.append(_tlv_u32(TLV_COMPONENT_VERSION, 1))
        items.append(_tlv_str(TLV_COMPONENT_ID, c.get("component_id", "")))
        items.append(_tlv_str(TLV_COMPONENT_VERSTR, c.get("component_version", "")))
        items.append(_tlv_u8(TLV_COMPONENT_KIND, _component_kind_u8(c.get("component_kind"))))
        items.append(_tlv_u32(TLV_COMPONENT_FLAGS, int(c.get("flags") or 0)))

        for d in c.get("dependencies", []) or []:
            dd_items = []
            dd_items.append(_tlv_u32(TLV_DEP_VERSION, 1))
            dd_items.append(_tlv_str(TLV_DEP_COMPONENT_ID, d.get("id", "")))
            dd_items.append(_tlv_u8(TLV_DEP_CONSTRAINT_KIND, _dep_constraint_kind_u8(d.get("constraint", "any"))))
            dep_ver = (d.get("version") or "").strip()
            if dep_ver:
                dd_items.append(_tlv_str(TLV_DEP_CONSTRAINT_VERSION, dep_ver))
            items.append(_tlv(TLV_DEPENDENCY, b"".join(dd_items)))

        for x in c.get("conflicts", []) or []:
            items.append(_tlv_str(TLV_CONFLICT, _norm_id(x)))

        for p in c.get("payloads", []) or []:
            pp_items = []
            pp_items.append(_tlv_u32(TLV_PAYLOAD_VERSION, 1))
            pp_items.append(_tlv_u8(TLV_PAYLOAD_KIND, _payload_kind_u8(p.get("kind"))))
            path = _norm_path(p.get("path") or "")
            if path:
                pp_items.append(_tlv_str(TLV_PAYLOAD_PATH, path))
            pp_items.append(_tlv(TLV_PAYLOAD_SHA256, _parse_sha256_hex(p.get("sha256"))))
            size = p.get("size")
            if size not in (None, "", "AUTO", "auto"):
                pp_items.append(_tlv_u64(TLV_PAYLOAD_SIZE, int(size)))
            items.append(_tlv(TLV_PAYLOAD, b"".join(pp_items)))

        for a in c.get("actions", []) or []:
            aa_items = []
            aa_items.append(_tlv_u32(TLV_ACTION_VERSION, 1))
            aa_items.append(_tlv_u8(TLV_ACTION_KIND, _action_kind_u8(a.get("kind"))))
            aa_items.append(_tlv_str(TLV_ACTION_APP_ID, _norm_id(a.get("app_id") or "")))
            aa_items.append(_tlv_str(TLV_ACTION_DISPLAY_NAME, a.get("display_name") or ""))
            aa_items.append(_tlv_str(TLV_ACTION_EXEC_RELPATH, _norm_path(a.get("exec_relpath") or "")))
            aa_items.append(_tlv_str(TLV_ACTION_ARGUMENTS, a.get("arguments") or ""))
            aa_items.append(_tlv_str(TLV_ACTION_ICON_RELPATH, _norm_path(a.get("icon_relpath") or "")))
            aa_items.append(_tlv_str(TLV_ACTION_EXTENSION, a.get("extension") or ""))
            aa_items.append(_tlv_str(TLV_ACTION_PROTOCOL, a.get("protocol") or ""))
            aa_items.append(_tlv_str(TLV_ACTION_MARKER_RELPATH, _norm_path(a.get("marker_relpath") or "")))
            aa_items.append(_tlv_str(TLV_ACTION_CAPABILITY_ID, _norm_id(a.get("capability_id") or "")))
            aa_items.append(_tlv_str(TLV_ACTION_CAPABILITY_VALUE, a.get("capability_value") or ""))
            aa_items.append(_tlv_str(TLV_ACTION_PUBLISHER, a.get("publisher") or ""))
            items.append(_tlv(TLV_ACTION, b"".join(aa_items)))

        root_items.append(_tlv(TLV_COMPONENT, b"".join(items)))

    if "uninstall_policy" in m and m["uninstall_policy"] is not None:
        up = m.get("uninstall_policy") or {}
        up_items = []
        up_items.append(_tlv_u32(TLV_POLICY_VERSION, 1))
        up_items.append(_tlv_u8(TLV_POLICY_REMOVE_OWNED, int(up.get("remove_owned_files") or 0)))
        up_items.append(_tlv_u8(TLV_POLICY_PRESERVE_USER_DATA, int(up.get("preserve_user_data") or 0)))
        up_items.append(_tlv_u8(TLV_POLICY_PRESERVE_CACHE, int(up.get("preserve_cache") or 0)))
        root_items.append(_tlv(TLV_UNINSTALL_POLICY, b"".join(up_items)))

    payload = _tlv(TLV_MANIFEST_ROOT, b"".join(root_items))
    return payload


def wrap_payload_to_dsumanifest(payload_bytes):
    if payload_bytes is None:
        payload_bytes = b""

    header_prefix = DSU_MAGIC + _u16(DSU_FORMAT_VERSION) + _u16(DSU_ENDIAN_MARKER_LE) + _u32(DSU_HEADER_SIZE) + _u32(len(payload_bytes))
    checksum = sum(bytearray(header_prefix)) & 0xFFFFFFFF
    header = header_prefix + _u32(checksum)
    if len(header) != DSU_HEADER_SIZE:
        raise RuntimeError("internal error: header size mismatch")
    return header + payload_bytes


def write_dsumanifest_from_json_file(json_path, out_path):
    with open(json_path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    payload = compile_dsumanifest_from_json(obj)
    data = wrap_payload_to_dsumanifest(payload)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(data)
    return 0


def sha256_bytes(data):
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def main(argv):
    import argparse

    ap = argparse.ArgumentParser(description="Compile a manifest JSON template into a binary *.dsumanifest file (DSUM v2 TLV).")
    ap.add_argument("--in", dest="in_path", required=True, help="Input manifest JSON file")
    ap.add_argument("--out", dest="out_path", required=True, help="Output *.dsumanifest path")
    args = ap.parse_args(argv)

    write_dsumanifest_from_json_file(args.in_path, args.out_path)
    print("wrote", os.path.abspath(args.out_path))
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main(sys.argv[1:]))

