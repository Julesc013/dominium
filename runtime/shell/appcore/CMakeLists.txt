cmake_minimum_required(VERSION 3.16)

add_library(appcore STATIC
    discover/appcore_discover.c
    profile/appcore_profile.c
    repox/appcore_repox.c
    invoke/appcore_invoke.c
    validate/appcore_validate.c
    command/command_registry.c
    command/command_dispatch.c
    output/appcore_output.c
    ui_bind/ui_command_binding_table.c
    ui_bind/ui_accessibility_map.c
)

target_include_directories(appcore PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/engine/include
)

set_target_properties(appcore PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_library(libs::appcore ALIAS appcore)
