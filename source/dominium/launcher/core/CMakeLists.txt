cmake_minimum_required(VERSION 3.16)

add_library(dominium_launcher_core STATIC
    src/launcher_core.cpp
    src/tlv/launcher_tlv.cpp
    src/profile/launcher_profile.cpp
    src/instance/launcher_instance.cpp
    src/artifact/launcher_artifact.cpp
    src/task/launcher_task.cpp
    src/audit/launcher_audit.cpp
)

target_include_directories(dominium_launcher_core
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

set_target_properties(dominium_launcher_core PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_executable(dominium_launcher_core_smoke
    tests/launcher_core_smoke.cpp
)

target_link_libraries(dominium_launcher_core_smoke PRIVATE
    dominium_launcher_core
)

target_include_directories(dominium_launcher_core_smoke PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

set_target_properties(dominium_launcher_core_smoke PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dominium_launcher_core_smoke COMMAND dominium_launcher_core_smoke)

