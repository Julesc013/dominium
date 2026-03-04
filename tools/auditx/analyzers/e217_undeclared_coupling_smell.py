"""E217 undeclared coupling smell analyzer."""

from __future__ import annotations

import json
import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E217_UNDECLARED_COUPLING_SMELL"
_COUPLING_REGISTRY_REL = "data/registries/coupling_contract_registry.json"
_REQUIRED_CONTRACTS = (
    ("energy_coupling", "ELEC", "THERM", "energy_transform"),
    ("energy_coupling", "FIELD", "THERM", "constitutive_model"),
    ("force_coupling", "THERM", "MECH", "constitutive_model"),
    ("force_coupling", "FIELD", "MOB", "field_policy"),
    ("info_coupling", "SIG", "SIG", "signal_policy"),
    ("force_coupling", "PHYS", "MOB", "constitutive_model"),
    ("energy_coupling", "FLUID", "THERM", "constitutive_model"),
    ("safety_coupling", "FLUID", "INT", "constitutive_model"),
    ("force_coupling", "FLUID", "MECH", "constitutive_model"),
)
_CROSS_DOMAIN_PATTERNS_BY_PREFIX = {
    "src/electric/": (
        re.compile(r"\bthermal_[a-z0-9_]+\b\s*=", re.IGNORECASE),
        re.compile(r"\bmech_[a-z0-9_]+\b\s*=", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']thermal_", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']mech_", re.IGNORECASE),
    ),
    "src/thermal/": (
        re.compile(r"\belec_[a-z0-9_]+\b\s*=", re.IGNORECASE),
        re.compile(r"\bmech_[a-z0-9_]+\b\s*=", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']elec_", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']mech_", re.IGNORECASE),
    ),
    "src/signals/": (
        re.compile(r"\bthermal_[a-z0-9_]+\b\s*=", re.IGNORECASE),
        re.compile(r"\belec_[a-z0-9_]+\b\s*=", re.IGNORECASE),
        re.compile(r"\bmech_[a-z0-9_]+\b\s*=", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']thermal_", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']elec_", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']mech_", re.IGNORECASE),
    ),
    "src/mobility/": (
        re.compile(r"\bthermal_[a-z0-9_]+\b\s*=", re.IGNORECASE),
        re.compile(r"\belec_[a-z0-9_]+\b\s*=", re.IGNORECASE),
        re.compile(r"\bmech_[a-z0-9_]+\b\s*=", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']thermal_", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']elec_", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']mech_", re.IGNORECASE),
    ),
    "src/fluid/": (
        re.compile(r"\bthermal_[a-z0-9_]+\b\s*=", re.IGNORECASE),
        re.compile(r"\bint_[a-z0-9_]+\b\s*=", re.IGNORECASE),
        re.compile(r"\bmech_[a-z0-9_]+\b\s*=", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']thermal_", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']int_", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']mech_", re.IGNORECASE),
    ),
}
_ALLOWED_FILES = {
    "src/models/model_engine.py",
    "tools/xstack/sessionx/process_runtime.py",
    "tools/xstack/repox/check.py",
}
_SCAN_PREFIXES = tuple(_CROSS_DOMAIN_PATTERNS_BY_PREFIX.keys())


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    abs_registry_path = os.path.join(repo_root, _COUPLING_REGISTRY_REL.replace("/", os.sep))
    try:
        payload = json.load(open(abs_registry_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.undeclared_coupling_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=_COUPLING_REGISTRY_REL,
                line=1,
                evidence=["coupling_contract_registry missing or invalid"],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-COUPLING-CONTRACT-REQUIRED", "INV-NO-UNDECLARED-COUPLING"],
                related_paths=[_COUPLING_REGISTRY_REL],
            )
        )
        return findings

    rows = list((dict(payload.get("record") or {})).get("coupling_contracts") or payload.get("coupling_contracts") or [])
    declared_contracts = set()
    declared_mechanisms = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        key = (
            str(row.get("coupling_class_id", "")).strip(),
            str(row.get("from_domain_id", "")).strip().upper(),
            str(row.get("to_domain_id", "")).strip().upper(),
            str(row.get("mechanism", "")).strip(),
        )
        if all(key):
            declared_contracts.add(key)
        mechanism_id = str(row.get("mechanism_id", "")).strip()
        if mechanism_id:
            declared_mechanisms.add(mechanism_id)

    for contract in _REQUIRED_CONTRACTS:
        if contract in declared_contracts:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.undeclared_coupling_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=_COUPLING_REGISTRY_REL,
                line=1,
                evidence=[
                    "required baseline coupling contract missing",
                    "{}:{}->{} ({})".format(contract[0], contract[1], contract[2], contract[3]),
                ],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-COUPLING-CONTRACT-REQUIRED", "INV-NO-UNDECLARED-COUPLING"],
                related_paths=[_COUPLING_REGISTRY_REL],
            )
        )

    for mechanism_id in (
        "transform.electrical_to_thermal",
        "model.phys_irradiance_heating_stub",
        "model.mech.fatigue.default",
        "field.profile_defined",
        "belief.default",
        "model.phys_gravity_force",
        "model.fluid_heat_exchanger_stub",
        "model.fluid_leak_flood_stub",
        "model.fluid_pressure_load_stub",
    ):
        if mechanism_id in declared_mechanisms:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.undeclared_coupling_smell",
                severity="VIOLATION",
                confidence=0.92,
                file_path=_COUPLING_REGISTRY_REL,
                line=1,
                evidence=["baseline coupling mechanism missing", mechanism_id],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-UNDECLARED-COUPLING"],
                related_paths=[_COUPLING_REGISTRY_REL],
            )
        )

    for root in _SCAN_PREFIXES:
        abs_root = os.path.join(repo_root, root.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
            for name in sorted(files):
                if not name.endswith(".py"):
                    continue
                rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                if rel_path in _ALLOWED_FILES:
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                active_patterns = ()
                for prefix, patterns in _CROSS_DOMAIN_PATTERNS_BY_PREFIX.items():
                    if rel_path.startswith(prefix):
                        active_patterns = patterns
                        break
                if not active_patterns:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not any(pattern.search(snippet) for pattern in active_patterns):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.undeclared_coupling_smell",
                            severity="RISK",
                            confidence=0.82,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "possible direct cross-domain coupling write detected",
                                snippet[:160],
                            ],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=["INV-NO-UNDECLARED-COUPLING"],
                            related_paths=[rel_path, _COUPLING_REGISTRY_REL],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
