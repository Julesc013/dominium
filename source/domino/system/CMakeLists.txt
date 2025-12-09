set(DOMINO_SYS_SOURCES
    sys.c
    core/domino_sys_core.c
    core/domino_term.c
    core/domino_ui_stub.c
    plat/null/sys_null.c
    plat/unix/posix/sys_posix.c
)

if(DSYS_BACKEND_CPM80)
    list(APPEND DOMINO_SYS_SOURCES
        plat/cpm80/cpm80_sys.c
    )
endif()
if(DSYS_BACKEND_CPM86)
    list(APPEND DOMINO_SYS_SOURCES
        plat/cpm86/cpm86_sys.c
    )
endif()

if(WIN32)
    list(APPEND DOMINO_SYS_SOURCES
        plat/windows/win32/sys_win32.c
    )
endif()
if(DOMINO_USE_CARBON_BACKEND OR DSYS_BACKEND_CARBON)
    list(APPEND DOMINO_SYS_SOURCES
        plat/carbon/carbon_sys.c
    )
endif()

add_library(domino_sys STATIC ${DOMINO_SYS_SOURCES})
target_include_directories(domino_sys
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/core
        ${CMAKE_CURRENT_SOURCE_DIR}/plat
)
target_compile_features(domino_sys PRIVATE c_std_90)
if(DSYS_BACKEND_CPM80)
    target_compile_definitions(domino_sys PRIVATE DSYS_BACKEND_CPM80)
endif()
if(DSYS_BACKEND_CPM86)
    target_compile_definitions(domino_sys PRIVATE DSYS_BACKEND_CPM86)
endif()
if(WIN32)
    target_link_libraries(domino_sys PRIVATE kernel32)
endif()
if(DOMINO_USE_CARBON_BACKEND OR DSYS_BACKEND_CARBON)
    target_compile_definitions(domino_sys PRIVATE DSYS_BACKEND_CARBON)
    find_library(CARBON_FRAMEWORK Carbon)
    if(CARBON_FRAMEWORK)
        target_link_libraries(domino_sys PRIVATE ${CARBON_FRAMEWORK})
    endif()
endif()
