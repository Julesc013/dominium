# Stub tooling target plus modcheck example.
add_custom_target(domino_tools ALL
    COMMAND ${CMAKE_COMMAND} -E echo "Tools are not fully wired yet (domino_assetc/domino_pack/domino_replay/domino_test)."
)

add_subdirectory(dominium_modcheck)
add_dependencies(domino_tools dominium_modcheck)
