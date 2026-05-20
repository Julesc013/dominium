cmake_minimum_required(VERSION 3.16)

add_library(runtime_shell STATIC
    discover/appcore_discover.c
    profile/appcore_profile.c
    ${CMAKE_SOURCE_DIR}/tools/repo/repox/shell/appcore_repox.c
    invoke/appcore_invoke.c
    ${CMAKE_SOURCE_DIR}/tools/validators/shell/appcore_validate.c
    command/command_registry.c
    command/command_dispatch.c
    output/appcore_output.c
    ${CMAKE_SOURCE_DIR}/tools/codegen/ui/bind/ui_command_binding_table.c
    ${CMAKE_SOURCE_DIR}/tools/codegen/ui/bind/ui_accessibility_map.c
)

target_include_directories(runtime_shell PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/engine/include
    ${CMAKE_SOURCE_DIR}/tools/codegen/ui/bind
    ${CMAKE_SOURCE_DIR}/tools/repo/repox/shell
    ${CMAKE_SOURCE_DIR}/tools/validators/shell
)

set_target_properties(runtime_shell PROPERTIES
    C_STANDARD 17
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_library(appcore ALIAS runtime_shell)
add_library(libs::appcore ALIAS runtime_shell)
