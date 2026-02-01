cmake_minimum_required(VERSION 3.16)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

file(MAKE_DIRECTORY "${CMAKE_BINARY_DIR}/tests")
set(_dom_gui_deps_report "${CMAKE_BINARY_DIR}/tests/gui_deps_report.txt")

set(_dom_gui_forbidden_tokens
    "SDL2::SDL2"
    "SDL2"
    "OpenGL::GL"
    "OpenGL::OpenGL"
    "opengl32"
    "GLU"
    "EGL"
    "GLESv2"
    "Vulkan::Vulkan"
    "vulkan-1"
    "vulkan"
    "d3d9"
    "d3d11"
    "dxgi"
    "X11"
    "Xrandr"
    "Xinerama"
    "Xcursor"
    "Xi"
    "wayland-client"
    "wayland-egl"
    "AppKit"
    "Cocoa"
    "UIKit"
    "Metal"
    "QuartzCore"
    "dom_render_backend_"
    "dom_platform_backend_"
    "dui"
    "dgui"
)

get_property(_dom_all_targets GLOBAL PROPERTY TARGETS)
set(_dom_test_targets "")
file(TO_CMAKE_PATH "${CMAKE_SOURCE_DIR}" _dom_repo_root)
string(REGEX REPLACE "([][+.*()^$?{}|\\\\])" "\\\\\\1" _dom_repo_root_regex "${_dom_repo_root}")
foreach(_dom_target IN LISTS _dom_all_targets)
    get_target_property(_dom_type ${_dom_target} TYPE)
    if(NOT _dom_type STREQUAL "EXECUTABLE")
        continue()
    endif()
    get_target_property(_dom_src_dir ${_dom_target} SOURCE_DIR)
    if(NOT _dom_src_dir OR _dom_src_dir STREQUAL "SOURCE_DIR-NOTFOUND")
        continue()
    endif()
    file(TO_CMAKE_PATH "${_dom_src_dir}" _dom_src_dir_norm)
    if(_dom_src_dir_norm MATCHES "^${_dom_repo_root_regex}/(tests|engine/tests|game/tests)(/|$)")
        list(APPEND _dom_test_targets ${_dom_target})
    endif()
endforeach()

file(WRITE "${_dom_gui_deps_report}" "report_version=1\n")
foreach(_dom_target IN LISTS _dom_test_targets)
    get_target_property(_dom_links ${_dom_target} LINK_LIBRARIES)
    if(_dom_links STREQUAL "LINK_LIBRARIES-NOTFOUND")
        set(_dom_links "")
    endif()
    set(_dom_links_clean "")
    foreach(_dom_link IN LISTS _dom_links)
        if(_dom_link STREQUAL "debug" OR _dom_link STREQUAL "optimized" OR _dom_link STREQUAL "general")
            continue()
        endif()
        list(APPEND _dom_links_clean "${_dom_link}")
        foreach(_dom_token IN LISTS _dom_gui_forbidden_tokens)
            string(FIND "${_dom_link}" "${_dom_token}" _dom_idx)
            if(NOT _dom_idx EQUAL -1)
                file(APPEND "${_dom_gui_deps_report}" "violation=${_dom_target}|${_dom_link}|${_dom_token}\n")
            endif()
        endforeach()
    endforeach()
    string(REPLACE ";" "," _dom_links_text "${_dom_links_clean}")
    file(APPEND "${_dom_gui_deps_report}" "target=${_dom_target}\n")
    file(APPEND "${_dom_gui_deps_report}" "links=${_dom_links_text}\n")
endforeach()

dom_add_testx(NAME build_test_gui_deps
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/test_gui_deps.py
        --report ${_dom_gui_deps_report}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

set(_dom_integration_report "${CMAKE_BINARY_DIR}/tests/integration_meta_report.txt")
get_property(_dom_renderer_backends GLOBAL PROPERTY DOM_REGISTERED_RENDER_BACKENDS)
if(NOT _dom_renderer_backends)
    set(_dom_renderer_backends "")
endif()
get_property(_dom_registered_renderer_tests_pre GLOBAL PROPERTY DOM_REGISTERED_RENDERER_TESTS)
set(_dom_renderer_tests_seen "")
if(_dom_registered_renderer_tests_pre)
    foreach(_dom_entry IN LISTS _dom_registered_renderer_tests_pre)
        string(REPLACE "|" ";" _dom_entry_parts "${_dom_entry}")
        list(LENGTH _dom_entry_parts _dom_entry_len)
        if(_dom_entry_len GREATER 0)
            list(GET _dom_entry_parts 0 _dom_entry_name)
            if(_dom_entry_name)
                list(APPEND _dom_renderer_tests_seen ${_dom_entry_name})
            endif()
        endif()
    endforeach()
endif()
foreach(_dom_backend IN LISTS _dom_renderer_backends)
    string(REPLACE "|" ";" _dom_backend_parts "${_dom_backend}")
    list(LENGTH _dom_backend_parts _dom_backend_len)
    if(_dom_backend_len GREATER 0)
        list(GET _dom_backend_parts 0 _dom_backend_name)
        if(_dom_backend_name)
            list(FIND _dom_renderer_tests_seen ${_dom_backend_name} _dom_backend_idx)
            if(_dom_backend_idx EQUAL -1)
                dom_register_renderer_tests(${_dom_backend_name}
                    renderer_backend_contracts
                    renderer_backend_contracts
                )
            endif()
        endif()
    endif()
endforeach()

dom_add_testx(NAME renderer_backend_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/renderer_backend_contracts.py
        --client $<TARGET_FILE:dominium_client>
        --launcher $<TARGET_FILE:launcher_cli>
        --report ${_dom_integration_report}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME integration_meta
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/integration_meta_test.py
        --report ${_dom_integration_report}
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME server_tools_operational
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/server_tools_operational_tests.py
        --server $<TARGET_FILE:dominium_server>
        --tools $<TARGET_FILE:dominium-tools>
        --temp-root ${CMAKE_BINARY_DIR}/tests/server_tools_operational
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME exploration_baseline
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/exploration_baseline_tests.py
        --client $<TARGET_FILE:dominium_client>
        --temp-root ${CMAKE_BINARY_DIR}/tests/exploration_baseline
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME exploration_scale_guard
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/exploration_scale_guard_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME exploration_scaling
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/exploration_scaling_tests.py
        --client $<TARGET_FILE:dominium_client>
        --temp-root ${CMAKE_BINARY_DIR}/tests/exploration_scaling
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME interaction_baseline
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/interaction_baseline_tests.py
        --client $<TARGET_FILE:dominium_client>
        --temp-root ${CMAKE_BINARY_DIR}/tests/interaction_baseline
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME interaction_scaling
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/interaction_scaling_tests.py
        --client $<TARGET_FILE:dominium_client>
        --temp-root ${CMAKE_BINARY_DIR}/tests/interaction_scaling
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME signal_baseline
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/signal_baseline_tests.py
        --client $<TARGET_FILE:dominium_client>
        --temp-root ${CMAKE_BINARY_DIR}/tests/signal_baseline
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME signal_scaling
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/signal_scaling_tests.py
        --client $<TARGET_FILE:dominium_client>
        --temp-root ${CMAKE_BINARY_DIR}/tests/signal_scaling
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME terrain_geometry
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/terrain_geometry_tests.py
        --tool $<TARGET_FILE:dom_tool_terrain>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME geology_fields
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/geology_field_tests.py
        --tool $<TARGET_FILE:dom_tool_geology>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME climate_fields
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/climate_field_tests.py
        --tool $<TARGET_FILE:dom_tool_climate>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME weather_events
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/weather_event_tests.py
        --tool $<TARGET_FILE:dom_tool_weather>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME energy_fields
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/energy_field_tests.py
        --tool $<TARGET_FILE:dom_tool_energy>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME heat_fields
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/heat_field_tests.py
        --tool $<TARGET_FILE:dom_tool_heat>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME fluid_fields
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/fluid_field_tests.py
        --tool $<TARGET_FILE:dom_tool_fluid>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME network_fields
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/network_field_tests.py
        --tool $<TARGET_FILE:dom_tool_network>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME hazard_fields
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/hazard_field_tests.py
        --tool $<TARGET_FILE:dom_tool_hazard>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME risk_fields
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/risk_field_tests.py
        --tool $<TARGET_FILE:dom_tool_risk>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME trust_fields
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/trust_field_tests.py
        --tool $<TARGET_FILE:dom_tool_trust>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME institution_fields
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/institution_field_tests.py
        --tool $<TARGET_FILE:dom_tool_institution>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME economy_fields
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/economy_field_tests.py
        --tool $<TARGET_FILE:dom_tool_economy>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME conflict_fields
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/conflict_field_tests.py
        --tool $<TARGET_FILE:dom_tool_conflict>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME history_fields
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/history_field_tests.py
        --tool $<TARGET_FILE:dom_tool_history>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME standard_fields
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/standard_field_tests.py
        --tool $<TARGET_FILE:dom_tool_standard>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME knowledge_fields
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/knowledge_field_tests.py
        --tool $<TARGET_FILE:dom_tool_knowledge>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME autonomy_fields
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/autonomy_field_tests.py
        --tool $<TARGET_FILE:dom_tool_autonomy>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME srz_fields
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/srz_field_tests.py
        --tool $<TARGET_FILE:dom_tool_srz>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME vegetation_fields
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/vegetation_field_tests.py
        --tool $<TARGET_FILE:dom_tool_vegetation>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME animal_agents
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/animal_agent_tests.py
        --tool $<TARGET_FILE:dom_tool_animal>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME structure_fields
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/structure_field_tests.py
        --tool $<TARGET_FILE:dom_tool_structure>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME travel_fields
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/travel_field_tests.py
        --tool $<TARGET_FILE:dom_tool_travel>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME mining_fields
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/mining_field_tests.py
        --tool $<TARGET_FILE:dom_tool_mining>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME crafting_fields
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/crafting_field_tests.py
        --tool $<TARGET_FILE:dom_tool_crafting>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

get_property(_dom_registered_products GLOBAL PROPERTY DOM_REGISTERED_PRODUCTS)
get_property(_dom_registered_product_tests GLOBAL PROPERTY DOM_REGISTERED_PRODUCT_CLI_TESTS)
get_property(_dom_registered_renderer_tests GLOBAL PROPERTY DOM_REGISTERED_RENDERER_TESTS)
get_property(_dom_registered_platform_backends GLOBAL PROPERTY DOM_REGISTERED_PLATFORM_BACKENDS)
get_property(_dom_registered_testx_tests GLOBAL PROPERTY DOM_REGISTERED_TESTX_TESTS)
if(NOT _dom_registered_products)
    set(_dom_registered_products "")
endif()
if(NOT _dom_registered_product_tests)
    set(_dom_registered_product_tests "")
endif()
if(NOT _dom_registered_renderer_tests)
    set(_dom_registered_renderer_tests "")
endif()
if(NOT _dom_registered_platform_backends)
    set(_dom_registered_platform_backends "")
endif()
if(NOT _dom_registered_testx_tests)
    set(_dom_registered_testx_tests "")
endif()

file(WRITE "${_dom_integration_report}" "report_version=1\n")
file(APPEND "${_dom_integration_report}" "registered_products=${_dom_registered_products}\n")
file(APPEND "${_dom_integration_report}" "registered_product_cli_tests=${_dom_registered_product_tests}\n")
file(APPEND "${_dom_integration_report}" "registered_renderer_backends=${_dom_renderer_backends}\n")
file(APPEND "${_dom_integration_report}" "registered_renderer_tests=${_dom_registered_renderer_tests}\n")
file(APPEND "${_dom_integration_report}" "registered_platform_backends=${_dom_registered_platform_backends}\n")
file(APPEND "${_dom_integration_report}" "registered_testx_tests=${_dom_registered_testx_tests}\n")
