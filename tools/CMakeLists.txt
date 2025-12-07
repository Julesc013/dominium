# Stub tooling target to keep the new tree compiling.
add_custom_target(domino_tools ALL
    COMMAND ${CMAKE_COMMAND} -E echo "Tools are not wired yet (domino_assetc/domino_pack/domino_replay/domino_test)."
)
