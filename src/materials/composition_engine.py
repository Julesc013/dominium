"""Deterministic material composition validation and batch helpers."""

from __future__ import annotations

from typing import Dict, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from .dimension_engine import fixed_point_config_from_policy


REFUSAL_MATERIAL_INVALID_COMPOSITION = "refusal.material.invalid_composition"
REFUSAL_MATERIAL_MASS_FRACTION_MISMATCH = "refusal.material.mass_fraction_mismatch"
REFUSAL_MATERIAL_DIMENSION_MISMATCH = "refusal.material.dimension_mismatch"

DEFAULT_FRACTION_SCALE = 1 << 24
DEFAULT_FRACTION_TOLERANCE_RAW = 1


class CompositionError(ValueError):
    """Deterministic material composition refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code)
        self.details = dict(details or {})


def _rows_by_id(rows: object, key_field: str) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    if not isinstance(rows, list):
        return out
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get(key_field, ""))):
        key = str(row.get(key_field, "")).strip()
        if key:
            out[key] = dict(row)
    return out


def _scale_from_policy(numeric_policy: Mapping[str, object] | None) -> int:
    policy = fixed_point_config_from_policy(numeric_policy)
    return int(policy.scale)


def _round_div_away_from_zero(numerator: int, denominator: int) -> int:
    if int(denominator) == 0:
        raise CompositionError(
            REFUSAL_MATERIAL_INVALID_COMPOSITION,
            "division by zero in composition normalization",
            {"denominator": str(denominator)},
        )
    n = int(numerator)
    d = int(denominator)
    sign = -1 if (n < 0) ^ (d < 0) else 1
    abs_n = abs(n)
    abs_d = abs(d)
    quotient = abs_n // abs_d
    remainder = abs_n % abs_d
    if remainder * 2 >= abs_d:
        quotient += 1
    return int(sign * quotient)


def validate_element_registry(element_registry: Mapping[str, object]) -> Dict[str, dict]:
    rows = _rows_by_id((element_registry or {}).get("elements"), "element_id")
    if not rows:
        raise CompositionError(
            REFUSAL_MATERIAL_INVALID_COMPOSITION,
            "element registry is empty",
            {"registry": "element_registry"},
        )
    for element_id, row in sorted(rows.items()):
        molar_mass_raw = int(row.get("molar_mass_raw", 0) or 0)
        if molar_mass_raw <= 0:
            raise CompositionError(
                REFUSAL_MATERIAL_INVALID_COMPOSITION,
                "element molar_mass_raw must be > 0",
                {"element_id": str(element_id)},
            )
        atomic_number = row.get("atomic_number")
        if atomic_number is not None and int(atomic_number) <= 0:
            raise CompositionError(
                REFUSAL_MATERIAL_INVALID_COMPOSITION,
                "element atomic_number must be null or >= 1",
                {"element_id": str(element_id), "atomic_number": int(atomic_number)},
            )
    return dict(rows)


def derive_compound_molar_mass(
    compound_row: Mapping[str, object],
    *,
    element_registry: Mapping[str, object],
) -> int:
    element_rows = validate_element_registry(element_registry)
    composition = dict((compound_row or {}).get("composition") or {})
    if not composition:
        raise CompositionError(
            REFUSAL_MATERIAL_INVALID_COMPOSITION,
            "compound composition is empty",
            {"compound_id": str((compound_row or {}).get("compound_id", ""))},
        )
    molar_mass_raw = 0
    for element_id in sorted(composition.keys()):
        token = str(element_id).strip()
        ratio = int(composition.get(element_id, 0) or 0)
        element_row = dict(element_rows.get(token) or {})
        if not token or not element_row or ratio <= 0:
            raise CompositionError(
                REFUSAL_MATERIAL_INVALID_COMPOSITION,
                "compound composition contains invalid element reference",
                {"compound_id": str((compound_row or {}).get("compound_id", "")), "element_id": token},
            )
        molar_mass_raw += int(ratio) * int(element_row.get("molar_mass_raw", 0) or 0)
    if molar_mass_raw <= 0:
        raise CompositionError(
            REFUSAL_MATERIAL_INVALID_COMPOSITION,
            "compound derived molar_mass_raw must be > 0",
            {"compound_id": str((compound_row or {}).get("compound_id", ""))},
        )
    return int(molar_mass_raw)


def validate_compound_composition(
    compound_row: Mapping[str, object],
    *,
    element_registry: Mapping[str, object],
    numeric_policy: Mapping[str, object] | None = None,
) -> Dict[str, object]:
    element_rows = validate_element_registry(element_registry)
    row = dict(compound_row or {})
    compound_id = str(row.get("compound_id", "")).strip()
    if not compound_id:
        raise CompositionError(
            REFUSAL_MATERIAL_INVALID_COMPOSITION,
            "compound_id is missing",
            {},
        )
    composition = dict(row.get("composition") or {})
    if not composition:
        raise CompositionError(
            REFUSAL_MATERIAL_INVALID_COMPOSITION,
            "compound composition is empty",
            {"compound_id": compound_id},
        )

    normalized_composition: Dict[str, int] = {}
    for element_id in sorted(composition.keys()):
        token = str(element_id).strip()
        ratio = int(composition.get(element_id, 0) or 0)
        if not token or ratio <= 0:
            continue
        if token not in element_rows:
            raise CompositionError(
                REFUSAL_MATERIAL_INVALID_COMPOSITION,
                "compound references unknown element",
                {"compound_id": compound_id, "element_id": token},
            )
        normalized_composition[token] = int(ratio)
    if not normalized_composition:
        raise CompositionError(
            REFUSAL_MATERIAL_INVALID_COMPOSITION,
            "compound composition has no positive ratios",
            {"compound_id": compound_id},
        )

    molar_mass_mode = str(row.get("molar_mass_mode", "derived")).strip() or "derived"
    declared_molar_mass_raw = int(row.get("molar_mass_raw", 0) or 0)
    derived_molar_mass_raw = derive_compound_molar_mass(
        {"compound_id": compound_id, "composition": normalized_composition},
        element_registry=element_registry,
    )
    molar_mass_raw = int(declared_molar_mass_raw) if molar_mass_mode == "declared" and declared_molar_mass_raw > 0 else int(derived_molar_mass_raw)
    if molar_mass_raw <= 0:
        raise CompositionError(
            REFUSAL_MATERIAL_INVALID_COMPOSITION,
            "compound molar_mass_raw is invalid",
            {"compound_id": compound_id},
        )

    scale = _scale_from_policy(numeric_policy) if numeric_policy else DEFAULT_FRACTION_SCALE
    fractions_raw: Dict[str, int] = {}
    assigned = 0
    element_ids = sorted(normalized_composition.keys())
    for idx, element_id in enumerate(element_ids):
        ratio = int(normalized_composition.get(element_id, 0) or 0)
        molar_component = int(ratio) * int((element_rows.get(element_id) or {}).get("molar_mass_raw", 0) or 0)
        if idx < len(element_ids) - 1:
            fraction_raw = _round_div_away_from_zero(molar_component * int(scale), int(molar_mass_raw))
            fractions_raw[element_id] = int(fraction_raw)
            assigned += int(fraction_raw)
        else:
            fractions_raw[element_id] = int(scale - assigned)
    fraction_sum_raw = sum(int(value) for value in fractions_raw.values())
    if int(fraction_sum_raw) != int(scale):
        raise CompositionError(
            REFUSAL_MATERIAL_MASS_FRACTION_MISMATCH,
            "compound normalized mass fractions failed to sum to canonical scale",
            {"compound_id": compound_id, "fraction_sum_raw": int(fraction_sum_raw), "scale": int(scale)},
        )

    out = dict(row)
    out["compound_id"] = compound_id
    out["composition"] = dict(normalized_composition)
    out["molar_mass_mode"] = str("declared" if molar_mass_mode == "declared" and declared_molar_mass_raw > 0 else "derived")
    out["molar_mass_raw"] = int(molar_mass_raw)
    out["mass_fractions_raw"] = dict(fractions_raw)
    out["mass_fraction_sum_raw"] = int(fraction_sum_raw)
    return out


def validate_mixture_composition(
    mixture_row: Mapping[str, object],
    *,
    numeric_policy: Mapping[str, object] | None = None,
    tolerance_raw: int = DEFAULT_FRACTION_TOLERANCE_RAW,
) -> Dict[str, object]:
    row = dict(mixture_row or {})
    mixture_id = str(row.get("mixture_id", "")).strip()
    if not mixture_id:
        raise CompositionError(
            REFUSAL_MATERIAL_INVALID_COMPOSITION,
            "mixture_id is missing",
            {},
        )
    components = dict(row.get("components") or {})
    if not components:
        raise CompositionError(
            REFUSAL_MATERIAL_INVALID_COMPOSITION,
            "mixture components are empty",
            {"mixture_id": mixture_id},
        )

    normalized_components: Dict[str, int] = {}
    for component_id in sorted(components.keys()):
        token = str(component_id).strip()
        value_raw = int(components.get(component_id, 0) or 0)
        if token and value_raw > 0:
            normalized_components[token] = int(value_raw)
    if not normalized_components:
        raise CompositionError(
            REFUSAL_MATERIAL_INVALID_COMPOSITION,
            "mixture components contain no positive mass fractions",
            {"mixture_id": mixture_id},
        )

    scale = _scale_from_policy(numeric_policy) if numeric_policy else DEFAULT_FRACTION_SCALE
    fraction_sum_raw = sum(int(value) for value in normalized_components.values())
    if abs(int(fraction_sum_raw) - int(scale)) > int(tolerance_raw):
        raise CompositionError(
            REFUSAL_MATERIAL_MASS_FRACTION_MISMATCH,
            "mixture mass fractions do not sum to canonical scale within tolerance",
            {
                "mixture_id": mixture_id,
                "fraction_sum_raw": int(fraction_sum_raw),
                "scale": int(scale),
                "tolerance_raw": int(tolerance_raw),
            },
        )
    out = dict(row)
    out["mixture_id"] = mixture_id
    out["components"] = dict(normalized_components)
    out["mass_fraction_sum_raw"] = int(fraction_sum_raw)
    return out


def validate_material_class(
    material_row: Mapping[str, object],
    *,
    dimension_registry: Mapping[str, object],
    unit_registry: Mapping[str, object],
) -> Dict[str, object]:
    row = dict(material_row or {})
    material_id = str(row.get("material_id", "")).strip()
    if not material_id:
        raise CompositionError(
            REFUSAL_MATERIAL_INVALID_COMPOSITION,
            "material_id is missing",
            {},
        )
    dimensions = _rows_by_id((dimension_registry or {}).get("dimensions"), "dimension_id")
    units = _rows_by_id((unit_registry or {}).get("units"), "unit_id")

    def _validate_property(field: str, expected_dimension_id: str = "") -> dict:
        prop = row.get(field)
        if prop is None:
            return {}
        if not isinstance(prop, dict):
            raise CompositionError(
                REFUSAL_MATERIAL_DIMENSION_MISMATCH,
                "material property must be object",
                {"material_id": material_id, "field": field},
            )
        unit_id = str(prop.get("unit_id", "")).strip()
        dimension_id = str(prop.get("dimension_id", "")).strip()
        value_raw = int(prop.get("value_raw", 0) or 0)
        if not unit_id or not dimension_id:
            raise CompositionError(
                REFUSAL_MATERIAL_DIMENSION_MISMATCH,
                "material property missing unit_id or dimension_id",
                {"material_id": material_id, "field": field},
            )
        unit_row = dict(units.get(unit_id) or {})
        if not unit_row:
            raise CompositionError(
                REFUSAL_MATERIAL_DIMENSION_MISMATCH,
                "material property references unknown unit_id",
                {"material_id": material_id, "field": field, "unit_id": unit_id},
            )
        if dimension_id not in dimensions:
            raise CompositionError(
                REFUSAL_MATERIAL_DIMENSION_MISMATCH,
                "material property references unknown dimension_id",
                {"material_id": material_id, "field": field, "dimension_id": dimension_id},
            )
        if str(unit_row.get("dimension_id", "")).strip() != dimension_id:
            raise CompositionError(
                REFUSAL_MATERIAL_DIMENSION_MISMATCH,
                "material property unit dimension mismatch",
                {
                    "material_id": material_id,
                    "field": field,
                    "unit_id": unit_id,
                    "dimension_id": dimension_id,
                    "unit_dimension_id": str(unit_row.get("dimension_id", "")),
                },
            )
        if expected_dimension_id and dimension_id != str(expected_dimension_id):
            raise CompositionError(
                REFUSAL_MATERIAL_DIMENSION_MISMATCH,
                "material property has unexpected dimension_id",
                {"material_id": material_id, "field": field, "dimension_id": dimension_id},
            )
        return {"value_raw": int(value_raw), "dimension_id": dimension_id, "unit_id": unit_id}

    density = _validate_property("density", expected_dimension_id="dim.density")
    specific_energy = _validate_property("specific_energy", expected_dimension_id="dim.specific_energy")
    conductivity = _validate_property("conductivity") if row.get("conductivity") is not None else None
    heat_capacity = _validate_property("heat_capacity") if row.get("heat_capacity") is not None else None
    if not density or not specific_energy:
        raise CompositionError(
            REFUSAL_MATERIAL_DIMENSION_MISMATCH,
            "material density/specific_energy definitions are required",
            {"material_id": material_id},
        )
    out = dict(row)
    out["material_id"] = material_id
    out["density"] = dict(density)
    out["specific_energy"] = dict(specific_energy)
    out["conductivity"] = None if conductivity is None else dict(conductivity)
    out["heat_capacity"] = None if heat_capacity is None else dict(heat_capacity)
    return out


def create_material_batch(
    *,
    material_id: str,
    quantity_mass_raw: int,
    origin_process_id: str,
    origin_tick: int,
    parent_batch_ids: list[str] | None = None,
    quality_distribution: Mapping[str, object] | None = None,
) -> Dict[str, object]:
    material_token = str(material_id).strip()
    process_token = str(origin_process_id).strip()
    tick_value = int(origin_tick)
    mass_raw = int(quantity_mass_raw)
    if not material_token or not process_token or tick_value < 0 or mass_raw < 0:
        raise CompositionError(
            REFUSAL_MATERIAL_INVALID_COMPOSITION,
            "material batch inputs are invalid",
            {
                "material_id": material_token,
                "origin_process_id": process_token,
                "origin_tick": tick_value,
                "quantity_mass_raw": mass_raw,
            },
        )
    parents = sorted(set(str(item).strip() for item in list(parent_batch_ids or []) if str(item).strip()))
    quality = dict(quality_distribution or {})
    identity_payload = {
        "material_id": material_token,
        "quantity_mass_raw": int(mass_raw),
        "origin_process_id": process_token,
        "origin_tick": int(tick_value),
        "parent_batch_ids": list(parents),
        "quality_distribution": dict(quality),
    }
    digest = canonical_sha256(identity_payload)
    batch_id = "batch.{}".format(digest[:24])
    return {
        "schema_version": "1.0.0",
        "batch_id": str(batch_id),
        "material_id": material_token,
        "quantity_mass_raw": int(mass_raw),
        "origin_process_id": process_token,
        "origin_tick": int(tick_value),
        "parent_batch_ids": list(parents),
        "quality_distribution": dict(quality),
        "extensions": {},
    }
