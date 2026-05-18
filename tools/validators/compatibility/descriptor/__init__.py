"""CAP-NEG-1 deterministic endpoint descriptor helpers."""

from .descriptor_engine import (
    build_product_build_metadata,
    build_product_descriptor,
    descriptor_json_text,
    emit_product_descriptor,
    load_product_capability_defaults,
    product_capability_default_rows_by_id,
    product_descriptor_bin_names,
    write_descriptor_file,
)

__all__ = [
    "build_product_build_metadata",
    "build_product_descriptor",
    "descriptor_json_text",
    "emit_product_descriptor",
    "load_product_capability_defaults",
    "product_capability_default_rows_by_id",
    "product_descriptor_bin_names",
    "write_descriptor_file",
]
