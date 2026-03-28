"""FAST test: SOL-1 phase fraction follows emitter/receiver/viewer geometry."""

from __future__ import annotations

import sys


TEST_ID = "test_phase_fraction_matches_geometry"
TEST_TAGS = ["fast", "sol", "illumination", "geometry", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from astro.illumination.illumination_geometry_engine import (
        build_emitter_descriptor,
        build_illumination_view_artifact,
        build_receiver_descriptor,
    )
    from geo import build_position_ref

    viewer_ref = build_position_ref(object_id="object.viewer.fixture", frame_id="frame.sol1.fixture", local_position=[0, 0, 0])
    emitter_row = build_emitter_descriptor(
        emitter_id="emitter.fixture.star",
        object_id="object.star.fixture",
        luminosity_proxy_value=1000,
    )
    receiver_row = build_receiver_descriptor(
        receiver_id="receiver.fixture.body",
        object_id="object.moon.fixture",
        radius_km=1737,
        albedo_proxy_permille=120,
    )
    cases = (
        ("full", [0, 0, 0], [0, 0, 100], 0, 1000),
        ("half", [100, 0, 100], [0, 0, 100], 90_000, 500),
        ("new", [0, 0, 200], [0, 0, 100], 180_000, 0),
    )
    for label, emitter_position, receiver_position, expected_angle, expected_fraction in cases:
        artifact = build_illumination_view_artifact(
            tick=0,
            viewer_ref=viewer_ref,
            emitter_row=emitter_row,
            receiver_row=receiver_row,
            emitter_position_ref=build_position_ref(
                object_id="object.star.fixture",
                frame_id="frame.sol1.fixture",
                local_position=emitter_position,
            ),
            receiver_position_ref=build_position_ref(
                object_id="object.moon.fixture",
                frame_id="frame.sol1.fixture",
                local_position=receiver_position,
            ),
        )
        phase_angle = int(artifact.get("phase_angle", 0) or 0)
        illumination_fraction = int(artifact.get("illumination_fraction", 0) or 0)
        if phase_angle != int(expected_angle):
            return {
                "status": "fail",
                "message": "SOL-1 {}-phase angle drifted: expected {}, got {}".format(label, expected_angle, phase_angle),
            }
        if illumination_fraction != int(expected_fraction):
            return {
                "status": "fail",
                "message": "SOL-1 {}-phase illumination drifted: expected {}, got {}".format(
                    label,
                    expected_fraction,
                    illumination_fraction,
                ),
            }
    return {"status": "pass", "message": "SOL-1 phase fraction matches emitter/receiver/viewer geometry"}
