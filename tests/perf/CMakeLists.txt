cmake_minimum_required(VERSION 3.16)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

dom_add_testx(NAME perf_fixture_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/perf_fixture_contracts.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME perf_budget_regression
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/perf_budget_gate_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
        --temp-root ${CMAKE_BINARY_DIR}/tests/perf_budget
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME exploration_fixture_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/exploration_fixture_contracts.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME terrain_perf
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/terrain_perf_tests.py
        --tool $<TARGET_FILE:dom_tool_terrain>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME geology_perf
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/geology_perf_tests.py
        --tool $<TARGET_FILE:dom_tool_geology>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME climate_perf
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/climate_perf_tests.py
        --tool $<TARGET_FILE:dom_tool_climate>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME weather_perf
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/weather_perf_tests.py
        --tool $<TARGET_FILE:dom_tool_weather>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME energy_perf
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/energy_perf_tests.py
        --tool $<TARGET_FILE:dom_tool_energy>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME heat_perf
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/heat_perf_tests.py
        --tool $<TARGET_FILE:dom_tool_heat>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME fluid_perf
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/fluid_perf_tests.py
        --tool $<TARGET_FILE:dom_tool_fluid>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME network_perf
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/network_perf_tests.py
        --tool $<TARGET_FILE:dom_tool_network>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME hazard_perf
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/hazard_perf_tests.py
        --tool $<TARGET_FILE:dom_tool_hazard>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME risk_perf
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/risk_perf_tests.py
        --tool $<TARGET_FILE:dom_tool_risk>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME trust_perf
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/trust_perf_tests.py
        --tool $<TARGET_FILE:dom_tool_trust>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME institution_perf
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/institution_perf_tests.py
        --tool $<TARGET_FILE:dom_tool_institution>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME economy_perf
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/economy_perf_tests.py
        --tool $<TARGET_FILE:dom_tool_economy>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME conflict_perf
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/conflict_perf_tests.py
        --tool $<TARGET_FILE:dom_tool_conflict>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME history_perf
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/history_perf_tests.py
        --tool $<TARGET_FILE:dom_tool_history>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME knowledge_perf
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/knowledge_perf_tests.py
        --tool $<TARGET_FILE:dom_tool_knowledge>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME vegetation_perf
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/vegetation_perf_tests.py
        --tool $<TARGET_FILE:dom_tool_vegetation>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME animal_perf
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/animal_perf_tests.py
        --tool $<TARGET_FILE:dom_tool_animal>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME structure_perf
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/structure_perf_tests.py
        --tool $<TARGET_FILE:dom_tool_structure>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME travel_perf
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/travel_perf_tests.py
        --tool $<TARGET_FILE:dom_tool_travel>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME mining_perf
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/mining_perf_tests.py
        --tool $<TARGET_FILE:dom_tool_mining>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME crafting_perf
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/crafting_perf_tests.py
        --tool $<TARGET_FILE:dom_tool_crafting>
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)
