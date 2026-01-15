#!/usr/bin/env python3
"""
Generates the binary TLV schema for the temporary launcher dev UI (L-9-B).

Output:
  source/dominium/launcher/ui_schema/launcher_ui_v1.tlv
"""

from __future__ import annotations

import os
import struct


def u32le(v: int) -> bytes:
    return struct.pack("<I", v & 0xFFFFFFFF)


def u64le(v: int) -> bytes:
    return struct.pack("<Q", v & 0xFFFFFFFFFFFFFFFF)


def tlv(tag: int, payload: bytes) -> bytes:
    return u32le(tag) + u32le(len(payload)) + payload


def tlv_u32(tag: int, v: int) -> bytes:
    return tlv(tag, u32le(v))


def tlv_u64(tag: int, v: int) -> bytes:
    return tlv(tag, u64le(v))


def tlv_text(tag: int, s: str) -> bytes:
    return tlv(tag, s.encode("utf-8"))


# Tags (include/dui/dui_schema_tlv.h)
SCH1 = 0x53434831  # 'SCH1'
FORM = 0x464F524D  # 'FORM'
NODE = 0x4E4F4445  # 'NODE'

ID_2 = 0x49445F32  # 'ID_2'
KIND = 0x4B494E44  # 'KIND'
TEXT = 0x54455854  # 'TEXT'
ACTN = 0x4143544E  # 'ACTN'
BIND = 0x42494E44  # 'BIND'
FLGC = 0x464C4743  # 'FLGC'
CAPS = 0x43415053  # 'CAPS'
VISB = 0x56495342  # 'VISB'
CHIL = 0x4348494C  # 'CHIL'

# Node kinds (include/dui/dui_schema_tlv.h)
K_ROW = 1
K_COLUMN = 2
K_STACK = 3
K_LABEL = 10
K_BUTTON = 11
K_CHECKBOX = 12
K_LIST = 13
K_TEXT_FIELD = 14
K_PROGRESS = 15

# Caps (include/dui/dui_api_v1.h)
CAP_LABEL = 1 << 8
CAP_BUTTON = 1 << 9
CAP_CHECKBOX = 1 << 10
CAP_LIST = 1 << 11
CAP_TEXT_FIELD = 1 << 12
CAP_PROGRESS = 1 << 13
CAP_LAYOUT_ROW = 1 << 16
CAP_LAYOUT_COLUMN = 1 << 17
CAP_LAYOUT_STACK = 1 << 18

# Flags (include/dui/dui_schema_tlv.h)
FLAG_FOCUSABLE = 1 << 0
FLAG_FLEX = 1 << 1


def node(
    *,
    wid: int,
    kind: int,
    text: str | None = None,
    action_id: int | None = None,
    bind_id: int | None = None,
    flags: int | None = None,
    required_caps: int | None = None,
    visible_bind_id: int | None = None,
    children: bytes | None = None,
) -> bytes:
    payload = b""
    payload += tlv_u32(ID_2, wid)
    payload += tlv_u32(KIND, kind)
    if text:
        payload += tlv_text(TEXT, text)
    if action_id is not None and action_id != 0:
        payload += tlv_u32(ACTN, action_id)
    if bind_id is not None and bind_id != 0:
        payload += tlv_u32(BIND, bind_id)
    if flags is not None and flags != 0:
        payload += tlv_u32(FLGC, flags)
    if required_caps is not None and required_caps != 0:
        payload += tlv_u64(CAPS, required_caps)
    if visible_bind_id is not None and visible_bind_id != 0:
        payload += tlv_u32(VISB, visible_bind_id)
    if children:
        payload += tlv(CHIL, children)
    return tlv(NODE, payload)


# Widget IDs (must match the launcher UI code)
W_ROOT_STACK = 1000

W_MAIN_COL = 1100
W_HEADER_ROW = 1110
W_TITLE = 1111
W_HEADER_INFO = 1112

W_BODY_ROW = 1120
W_LEFT_COL = 1121
W_PANEL_COL = 1122

W_INST_LABEL = 1200
W_INST_SEARCH = 1201
W_INST_LIST = 1202
W_INST_HINT = 1203

W_TAB_ROW = 1300
W_TAB_PLAY_BTN = 1301
W_TAB_INST_BTN = 1302
W_TAB_PACKS_BTN = 1303
W_TAB_OPTIONS_BTN = 1304
W_TAB_LOGS_BTN = 1305

W_TAB_STACK = 1310
W_TAB_PLAY_PANEL = 1311
W_TAB_INST_PANEL = 1312
W_TAB_PACKS_PANEL = 1313
W_TAB_OPTIONS_PANEL = 1314
W_TAB_LOGS_PANEL = 1315

W_PLAY_ROW = 1400
W_PLAY_LEFT_COL = 1401
W_PLAY_NEWS_COL = 1402
W_PLAY_SELECTED = 1410
W_PLAY_PROFILE = 1411
W_PLAY_MANIFEST = 1412
W_PLAY_TARGET_LABEL = 1413
W_PLAY_TARGET_LIST = 1414
W_PLAY_OFFLINE = 1415
W_PLAY_BTN = 1416
W_SAFE_PLAY_BTN = 1417
W_VERIFY_BTN = 1418
W_PLAY_LAST_RUN = 1419
W_NEWS_LABEL = 1450
W_NEWS_LIST = 1451

W_INST_ACTIONS_LABEL = 1500
W_INST_CREATE_BTN = 1501
W_INST_CLONE_BTN = 1502
W_INST_DELETE_BTN = 1503
W_INST_IMPORT_LABEL = 1504
W_INST_IMPORT_PATH = 1505
W_INST_IMPORT_BTN = 1506
W_INST_EXPORT_LABEL = 1507
W_INST_EXPORT_PATH = 1508
W_INST_EXPORT_DEF_BTN = 1509
W_INST_EXPORT_BUNDLE_BTN = 1510
W_INST_MARK_KG_BTN = 1511
W_INST_PATHS_LIST = 1512

W_PACKS_LABEL = 1600
W_PACKS_LIST = 1601
W_PACKS_ENABLED = 1602
W_PACKS_POLICY_LABEL = 1603
W_PACKS_POLICY_LIST = 1604
W_PACKS_APPLY_BTN = 1605
W_PACKS_RESOLVED_LABEL = 1606
W_PACKS_RESOLVED = 1607
W_PACKS_ERROR = 1608

W_OPT_LABEL = 1700
W_OPT_GFX_LABEL = 1701
W_OPT_GFX_LIST = 1702
W_OPT_API_LABEL = 1703
W_OPT_API_FIELD = 1704
W_OPT_WINMODE_LABEL = 1705
W_OPT_WINMODE_LIST = 1706
W_OPT_RES_LABEL = 1707
W_OPT_WIDTH_FIELD = 1708
W_OPT_HEIGHT_FIELD = 1709
W_OPT_DPI_FIELD = 1710
W_OPT_MONITOR_FIELD = 1711
W_OPT_AUDIO_LABEL = 1712
W_OPT_INPUT_LABEL = 1713
W_OPT_RESET_BTN = 1714
W_OPT_DETAILS_BTN = 1715

W_LOGS_LABEL = 1800
W_LOGS_LAST_RUN = 1801
W_LOGS_ROW = 1802
W_LOGS_RUNS_LIST = 1803
W_LOGS_AUDIT_LIST = 1804
W_LOGS_DIAG_LABEL = 1805
W_LOGS_DIAG_OUT = 1806
W_LOGS_DIAG_BTN = 1807
W_LOGS_LOCS_LABEL = 1808
W_LOGS_LOCS_LIST = 1809

W_STATUS_ROW = 1900
W_STATUS_TEXT = 1901
W_STATUS_PROGRESS = 1902
W_STATUS_SELECTION = 1903

W_DIALOG_COL = 2000
W_DIALOG_TITLE = 2001
W_DIALOG_TEXT = 2002
W_DIALOG_LIST = 2003
W_DIALOG_BTN_ROW = 2004
W_DIALOG_OK = 2005
W_DIALOG_CANCEL = 2006


# Action IDs (must match the launcher UI code)
ACT_TAB_PLAY = 100
ACT_TAB_INST = 101
ACT_TAB_PACKS = 102
ACT_TAB_OPTIONS = 103
ACT_TAB_LOGS = 104

ACT_PLAY = 200
ACT_SAFE_PLAY = 201
ACT_VERIFY_REPAIR = 202

ACT_INST_CREATE = 300
ACT_INST_CLONE = 301
ACT_INST_DELETE = 302
ACT_INST_IMPORT = 303
ACT_INST_EXPORT_DEF = 304
ACT_INST_EXPORT_BUNDLE = 305
ACT_INST_MARK_KG = 306

ACT_PACKS_APPLY = 400

ACT_OPT_RESET = 500
ACT_OPT_DETAILS = 501

ACT_LOGS_DIAG = 600

ACT_DIALOG_OK = 900
ACT_DIALOG_CANCEL = 901


def build_schema() -> bytes:
    header_children = b"".join(
        [
            node(wid=W_TITLE, kind=K_LABEL, text="Dominium Dev Launcher", required_caps=CAP_LABEL),
            node(wid=W_HEADER_INFO, kind=K_LABEL, bind_id=W_HEADER_INFO, required_caps=CAP_LABEL),
        ]
    )
    header_row = node(wid=W_HEADER_ROW, kind=K_ROW, required_caps=CAP_LAYOUT_ROW, children=header_children)

    left_children = b"".join(
        [
            node(wid=W_INST_LABEL, kind=K_LABEL, text="Instances", required_caps=CAP_LABEL),
            node(wid=W_INST_SEARCH, kind=K_TEXT_FIELD, bind_id=W_INST_SEARCH, flags=FLAG_FOCUSABLE, required_caps=CAP_TEXT_FIELD),
            node(
                wid=W_INST_LIST,
                kind=K_LIST,
                bind_id=W_INST_LIST,
                flags=FLAG_FOCUSABLE | FLAG_FLEX,
                required_caps=CAP_LIST,
            ),
            node(wid=W_INST_HINT, kind=K_LABEL, bind_id=W_INST_HINT, required_caps=CAP_LABEL),
        ]
    )
    left_col = node(wid=W_LEFT_COL, kind=K_COLUMN, required_caps=CAP_LAYOUT_COLUMN, flags=FLAG_FLEX, children=left_children)

    tab_btns = b"".join(
        [
            node(wid=W_TAB_PLAY_BTN, kind=K_BUTTON, bind_id=W_TAB_PLAY_BTN, action_id=ACT_TAB_PLAY, flags=FLAG_FOCUSABLE, required_caps=CAP_BUTTON),
            node(wid=W_TAB_INST_BTN, kind=K_BUTTON, bind_id=W_TAB_INST_BTN, action_id=ACT_TAB_INST, flags=FLAG_FOCUSABLE, required_caps=CAP_BUTTON),
            node(wid=W_TAB_PACKS_BTN, kind=K_BUTTON, bind_id=W_TAB_PACKS_BTN, action_id=ACT_TAB_PACKS, flags=FLAG_FOCUSABLE, required_caps=CAP_BUTTON),
            node(wid=W_TAB_OPTIONS_BTN, kind=K_BUTTON, bind_id=W_TAB_OPTIONS_BTN, action_id=ACT_TAB_OPTIONS, flags=FLAG_FOCUSABLE, required_caps=CAP_BUTTON),
            node(wid=W_TAB_LOGS_BTN, kind=K_BUTTON, bind_id=W_TAB_LOGS_BTN, action_id=ACT_TAB_LOGS, flags=FLAG_FOCUSABLE, required_caps=CAP_BUTTON),
        ]
    )
    tab_row = node(wid=W_TAB_ROW, kind=K_ROW, required_caps=CAP_LAYOUT_ROW, children=tab_btns)

    play_left_children = b"".join(
        [
            node(wid=W_PLAY_SELECTED, kind=K_LABEL, bind_id=W_PLAY_SELECTED, required_caps=CAP_LABEL),
            node(wid=W_PLAY_PROFILE, kind=K_LABEL, bind_id=W_PLAY_PROFILE, required_caps=CAP_LABEL),
            node(wid=W_PLAY_MANIFEST, kind=K_LABEL, bind_id=W_PLAY_MANIFEST, required_caps=CAP_LABEL),
            node(wid=W_PLAY_TARGET_LABEL, kind=K_LABEL, text="Target", required_caps=CAP_LABEL),
            node(wid=W_PLAY_TARGET_LIST, kind=K_LIST, bind_id=W_PLAY_TARGET_LIST, flags=FLAG_FOCUSABLE, required_caps=CAP_LIST),
            node(wid=W_PLAY_OFFLINE, kind=K_CHECKBOX, text="Offline mode", bind_id=W_PLAY_OFFLINE, flags=FLAG_FOCUSABLE, required_caps=CAP_CHECKBOX),
            node(wid=W_PLAY_BTN, kind=K_BUTTON, text="Play", action_id=ACT_PLAY, flags=FLAG_FOCUSABLE, required_caps=CAP_BUTTON),
            node(wid=W_SAFE_PLAY_BTN, kind=K_BUTTON, text="Safe Mode Play", action_id=ACT_SAFE_PLAY, flags=FLAG_FOCUSABLE, required_caps=CAP_BUTTON),
            node(wid=W_VERIFY_BTN, kind=K_BUTTON, text="Verify / Repair", action_id=ACT_VERIFY_REPAIR, flags=FLAG_FOCUSABLE, required_caps=CAP_BUTTON),
            node(wid=W_PLAY_LAST_RUN, kind=K_LABEL, bind_id=W_PLAY_LAST_RUN, required_caps=CAP_LABEL),
        ]
    )
    play_left_col = node(wid=W_PLAY_LEFT_COL, kind=K_COLUMN, required_caps=CAP_LAYOUT_COLUMN, children=play_left_children)

    play_news_children = b"".join(
        [
            node(wid=W_NEWS_LABEL, kind=K_LABEL, text="News", required_caps=CAP_LABEL),
            node(wid=W_NEWS_LIST, kind=K_LIST, bind_id=W_NEWS_LIST, flags=FLAG_FOCUSABLE | FLAG_FLEX, required_caps=CAP_LIST),
        ]
    )
    play_news_col = node(wid=W_PLAY_NEWS_COL, kind=K_COLUMN, required_caps=CAP_LAYOUT_COLUMN, flags=FLAG_FLEX, children=play_news_children)

    play_row_children = b"".join([play_left_col, play_news_col])
    play_row = node(wid=W_PLAY_ROW, kind=K_ROW, required_caps=CAP_LAYOUT_ROW, flags=FLAG_FLEX, children=play_row_children)

    play_panel_children = b"".join([play_row])
    play_panel = node(
        wid=W_TAB_PLAY_PANEL,
        kind=K_COLUMN,
        required_caps=CAP_LAYOUT_COLUMN,
        visible_bind_id=W_TAB_PLAY_PANEL,
        flags=FLAG_FLEX,
        children=play_panel_children,
    )

    inst_panel_children = b"".join(
        [
            node(wid=W_INST_ACTIONS_LABEL, kind=K_LABEL, text="Instance Actions", required_caps=CAP_LABEL),
            node(wid=W_INST_CREATE_BTN, kind=K_BUTTON, text="Create from Selected (Template)", action_id=ACT_INST_CREATE, flags=FLAG_FOCUSABLE, required_caps=CAP_BUTTON),
            node(wid=W_INST_CLONE_BTN, kind=K_BUTTON, text="Clone Selected", action_id=ACT_INST_CLONE, flags=FLAG_FOCUSABLE, required_caps=CAP_BUTTON),
            node(wid=W_INST_DELETE_BTN, kind=K_BUTTON, text="Delete Selected (Soft)", action_id=ACT_INST_DELETE, flags=FLAG_FOCUSABLE, required_caps=CAP_BUTTON),
            node(wid=W_INST_IMPORT_LABEL, kind=K_LABEL, text="Import (path)", required_caps=CAP_LABEL),
            node(wid=W_INST_IMPORT_PATH, kind=K_TEXT_FIELD, bind_id=W_INST_IMPORT_PATH, flags=FLAG_FOCUSABLE, required_caps=CAP_TEXT_FIELD),
            node(wid=W_INST_IMPORT_BTN, kind=K_BUTTON, text="Import", action_id=ACT_INST_IMPORT, flags=FLAG_FOCUSABLE, required_caps=CAP_BUTTON),
            node(wid=W_INST_EXPORT_LABEL, kind=K_LABEL, text="Export (path)", required_caps=CAP_LABEL),
            node(wid=W_INST_EXPORT_PATH, kind=K_TEXT_FIELD, bind_id=W_INST_EXPORT_PATH, flags=FLAG_FOCUSABLE, required_caps=CAP_TEXT_FIELD),
            node(wid=W_INST_EXPORT_DEF_BTN, kind=K_BUTTON, text="Export Definition", action_id=ACT_INST_EXPORT_DEF, flags=FLAG_FOCUSABLE, required_caps=CAP_BUTTON),
            node(wid=W_INST_EXPORT_BUNDLE_BTN, kind=K_BUTTON, text="Export Bundle", action_id=ACT_INST_EXPORT_BUNDLE, flags=FLAG_FOCUSABLE, required_caps=CAP_BUTTON),
            node(wid=W_INST_MARK_KG_BTN, kind=K_BUTTON, text="Set Known-Good Marker", action_id=ACT_INST_MARK_KG, flags=FLAG_FOCUSABLE, required_caps=CAP_BUTTON),
            node(wid=W_INST_PATHS_LIST, kind=K_LIST, bind_id=W_INST_PATHS_LIST, flags=FLAG_FOCUSABLE | FLAG_FLEX, required_caps=CAP_LIST),
        ]
    )
    inst_panel = node(
        wid=W_TAB_INST_PANEL,
        kind=K_COLUMN,
        required_caps=CAP_LAYOUT_COLUMN,
        visible_bind_id=W_TAB_INST_PANEL,
        flags=FLAG_FLEX,
        children=inst_panel_children,
    )

    packs_panel_children = b"".join(
        [
            node(wid=W_PACKS_LABEL, kind=K_LABEL, bind_id=W_PACKS_LABEL, required_caps=CAP_LABEL),
            node(wid=W_PACKS_LIST, kind=K_LIST, bind_id=W_PACKS_LIST, flags=FLAG_FOCUSABLE | FLAG_FLEX, required_caps=CAP_LIST),
            node(wid=W_PACKS_ENABLED, kind=K_CHECKBOX, text="Enabled", bind_id=W_PACKS_ENABLED, flags=FLAG_FOCUSABLE, required_caps=CAP_CHECKBOX),
            node(wid=W_PACKS_POLICY_LABEL, kind=K_LABEL, text="Update policy", required_caps=CAP_LABEL),
            node(wid=W_PACKS_POLICY_LIST, kind=K_LIST, bind_id=W_PACKS_POLICY_LIST, flags=FLAG_FOCUSABLE, required_caps=CAP_LIST),
            node(wid=W_PACKS_APPLY_BTN, kind=K_BUTTON, text="Apply Changes", action_id=ACT_PACKS_APPLY, flags=FLAG_FOCUSABLE, required_caps=CAP_BUTTON),
            node(wid=W_PACKS_RESOLVED_LABEL, kind=K_LABEL, text="Resolved order", required_caps=CAP_LABEL),
            node(wid=W_PACKS_RESOLVED, kind=K_LABEL, bind_id=W_PACKS_RESOLVED, required_caps=CAP_LABEL),
            node(wid=W_PACKS_ERROR, kind=K_LABEL, bind_id=W_PACKS_ERROR, required_caps=CAP_LABEL),
        ]
    )
    packs_panel = node(
        wid=W_TAB_PACKS_PANEL,
        kind=K_COLUMN,
        required_caps=CAP_LAYOUT_COLUMN,
        visible_bind_id=W_TAB_PACKS_PANEL,
        flags=FLAG_FLEX,
        children=packs_panel_children,
    )

    opt_panel_children = b"".join(
        [
            node(wid=W_OPT_LABEL, kind=K_LABEL, text="Options", required_caps=CAP_LABEL),
            node(wid=W_OPT_GFX_LABEL, kind=K_LABEL, text="GFX backend", required_caps=CAP_LABEL),
            node(wid=W_OPT_GFX_LIST, kind=K_LIST, bind_id=W_OPT_GFX_LIST, flags=FLAG_FOCUSABLE, required_caps=CAP_LIST),
            node(wid=W_OPT_API_LABEL, kind=K_LABEL, text="Renderer API (text)", required_caps=CAP_LABEL),
            node(wid=W_OPT_API_FIELD, kind=K_TEXT_FIELD, bind_id=W_OPT_API_FIELD, flags=FLAG_FOCUSABLE, required_caps=CAP_TEXT_FIELD),
            node(wid=W_OPT_WINMODE_LABEL, kind=K_LABEL, text="Window mode", required_caps=CAP_LABEL),
            node(wid=W_OPT_WINMODE_LIST, kind=K_LIST, bind_id=W_OPT_WINMODE_LIST, flags=FLAG_FOCUSABLE, required_caps=CAP_LIST),
            node(wid=W_OPT_RES_LABEL, kind=K_LABEL, text="Width / Height / DPI / Monitor", required_caps=CAP_LABEL),
            node(wid=W_OPT_WIDTH_FIELD, kind=K_TEXT_FIELD, bind_id=W_OPT_WIDTH_FIELD, flags=FLAG_FOCUSABLE, required_caps=CAP_TEXT_FIELD),
            node(wid=W_OPT_HEIGHT_FIELD, kind=K_TEXT_FIELD, bind_id=W_OPT_HEIGHT_FIELD, flags=FLAG_FOCUSABLE, required_caps=CAP_TEXT_FIELD),
            node(wid=W_OPT_DPI_FIELD, kind=K_TEXT_FIELD, bind_id=W_OPT_DPI_FIELD, flags=FLAG_FOCUSABLE, required_caps=CAP_TEXT_FIELD),
            node(wid=W_OPT_MONITOR_FIELD, kind=K_TEXT_FIELD, bind_id=W_OPT_MONITOR_FIELD, flags=FLAG_FOCUSABLE, required_caps=CAP_TEXT_FIELD),
            node(wid=W_OPT_AUDIO_LABEL, kind=K_LABEL, bind_id=W_OPT_AUDIO_LABEL, required_caps=CAP_LABEL),
            node(wid=W_OPT_INPUT_LABEL, kind=K_LABEL, bind_id=W_OPT_INPUT_LABEL, required_caps=CAP_LABEL),
            node(wid=W_OPT_RESET_BTN, kind=K_BUTTON, text="Reset graphics overrides", action_id=ACT_OPT_RESET, flags=FLAG_FOCUSABLE, required_caps=CAP_BUTTON),
            node(wid=W_OPT_DETAILS_BTN, kind=K_BUTTON, text="View effective config", action_id=ACT_OPT_DETAILS, flags=FLAG_FOCUSABLE, required_caps=CAP_BUTTON),
        ]
    )
    opt_panel = node(
        wid=W_TAB_OPTIONS_PANEL,
        kind=K_COLUMN,
        required_caps=CAP_LAYOUT_COLUMN,
        visible_bind_id=W_TAB_OPTIONS_PANEL,
        flags=FLAG_FLEX,
        children=opt_panel_children,
    )

    logs_row_children = b"".join(
        [
            node(wid=W_LOGS_RUNS_LIST, kind=K_LIST, bind_id=W_LOGS_RUNS_LIST, flags=FLAG_FOCUSABLE | FLAG_FLEX, required_caps=CAP_LIST),
            node(wid=W_LOGS_AUDIT_LIST, kind=K_LIST, bind_id=W_LOGS_AUDIT_LIST, flags=FLAG_FOCUSABLE | FLAG_FLEX, required_caps=CAP_LIST),
        ]
    )
    logs_row = node(wid=W_LOGS_ROW, kind=K_ROW, required_caps=CAP_LAYOUT_ROW, flags=FLAG_FLEX, children=logs_row_children)

    logs_panel_children = b"".join(
        [
            node(wid=W_LOGS_LABEL, kind=K_LABEL, text="Logs / Diagnostics", required_caps=CAP_LABEL),
            node(wid=W_LOGS_LAST_RUN, kind=K_LABEL, bind_id=W_LOGS_LAST_RUN, required_caps=CAP_LABEL),
            logs_row,
            node(wid=W_LOGS_DIAG_LABEL, kind=K_LABEL, text="Diagnostics bundle output (optional)", required_caps=CAP_LABEL),
            node(wid=W_LOGS_DIAG_OUT, kind=K_TEXT_FIELD, bind_id=W_LOGS_DIAG_OUT, flags=FLAG_FOCUSABLE, required_caps=CAP_TEXT_FIELD),
            node(wid=W_LOGS_DIAG_BTN, kind=K_BUTTON, text="Generate diagnostics bundle", action_id=ACT_LOGS_DIAG, flags=FLAG_FOCUSABLE, required_caps=CAP_BUTTON),
            node(wid=W_LOGS_LOCS_LABEL, kind=K_LABEL, text="Locations", required_caps=CAP_LABEL),
            node(wid=W_LOGS_LOCS_LIST, kind=K_LIST, bind_id=W_LOGS_LOCS_LIST, flags=FLAG_FOCUSABLE, required_caps=CAP_LIST),
        ]
    )
    logs_panel = node(
        wid=W_TAB_LOGS_PANEL,
        kind=K_COLUMN,
        required_caps=CAP_LAYOUT_COLUMN,
        visible_bind_id=W_TAB_LOGS_PANEL,
        flags=FLAG_FLEX,
        children=logs_panel_children,
    )

    tab_stack_children = b"".join([play_panel, inst_panel, packs_panel, opt_panel, logs_panel])
    tab_stack = node(wid=W_TAB_STACK, kind=K_STACK, required_caps=CAP_LAYOUT_STACK, flags=FLAG_FLEX, children=tab_stack_children)

    panel_children = b"".join([tab_row, tab_stack])
    panel_col = node(wid=W_PANEL_COL, kind=K_COLUMN, required_caps=CAP_LAYOUT_COLUMN, flags=FLAG_FLEX, children=panel_children)

    body_children = b"".join([left_col, panel_col])
    body_row = node(wid=W_BODY_ROW, kind=K_ROW, required_caps=CAP_LAYOUT_ROW, flags=FLAG_FLEX, children=body_children)

    status_children = b"".join(
        [
            node(wid=W_STATUS_TEXT, kind=K_LABEL, bind_id=W_STATUS_TEXT, required_caps=CAP_LABEL),
            node(wid=W_STATUS_PROGRESS, kind=K_PROGRESS, bind_id=W_STATUS_PROGRESS, required_caps=CAP_PROGRESS),
            node(wid=W_STATUS_SELECTION, kind=K_LABEL, bind_id=W_STATUS_SELECTION, required_caps=CAP_LABEL),
        ]
    )
    status_row = node(wid=W_STATUS_ROW, kind=K_ROW, required_caps=CAP_LAYOUT_ROW, children=status_children)

    main_children = b"".join([header_row, body_row, status_row])
    main_col = node(wid=W_MAIN_COL, kind=K_COLUMN, required_caps=CAP_LAYOUT_COLUMN, children=main_children)

    dialog_btns = b"".join(
        [
            node(wid=W_DIALOG_OK, kind=K_BUTTON, text="OK", action_id=ACT_DIALOG_OK, flags=FLAG_FOCUSABLE, required_caps=CAP_BUTTON),
            node(wid=W_DIALOG_CANCEL, kind=K_BUTTON, text="Cancel", action_id=ACT_DIALOG_CANCEL, flags=FLAG_FOCUSABLE, required_caps=CAP_BUTTON),
        ]
    )
    dialog_btn_row = node(wid=W_DIALOG_BTN_ROW, kind=K_ROW, required_caps=CAP_LAYOUT_ROW, children=dialog_btns)

    dialog_children = b"".join(
        [
            node(wid=W_DIALOG_TITLE, kind=K_LABEL, bind_id=W_DIALOG_TITLE, required_caps=CAP_LABEL),
            node(wid=W_DIALOG_TEXT, kind=K_LABEL, bind_id=W_DIALOG_TEXT, required_caps=CAP_LABEL),
            node(wid=W_DIALOG_LIST, kind=K_LIST, bind_id=W_DIALOG_LIST, flags=FLAG_FOCUSABLE | FLAG_FLEX, required_caps=CAP_LIST),
            dialog_btn_row,
        ]
    )
    dialog_col = node(
        wid=W_DIALOG_COL,
        kind=K_COLUMN,
        required_caps=CAP_LAYOUT_COLUMN,
        visible_bind_id=W_DIALOG_COL,
        flags=FLAG_FLEX,
        children=dialog_children,
    )

    root_children = b"".join([main_col, dialog_col])
    root = node(wid=W_ROOT_STACK, kind=K_STACK, required_caps=CAP_LAYOUT_STACK, children=root_children)

    form = tlv(FORM, root)
    schema = tlv(SCH1, form)
    return schema


def main() -> int:
    schema = build_schema()
    out_path = os.path.join("source", "dominium", "launcher", "ui_schema", "launcher_ui_v1.tlv")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(schema)
    print(f"Wrote {out_path} ({len(schema)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

