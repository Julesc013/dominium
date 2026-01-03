# Stub tooling target plus modcheck example.
add_custom_target(domino_tools ALL
    COMMAND ${CMAKE_COMMAND} -E echo "Tools are not fully wired yet (domino_assetc/domino_pack/domino_replay/domino_test)."
)

if(TARGET dominium_modcheck)
    add_dependencies(domino_tools dominium_modcheck)
endif()

add_subdirectory(ui_editor)
add_subdirectory(ui_preview_host)
add_subdirectory(tool_editor)
add_subdirectory(dist_seed)
