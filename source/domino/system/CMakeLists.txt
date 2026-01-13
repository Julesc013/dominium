set(DOMINO_SYS_SOURCES
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
if(DSYS_BACKEND_DOS16)
    list(APPEND DOMINO_SYS_SOURCES
        plat/dos16/dos16_sys.c
    )
endif()
if(DSYS_BACKEND_DOS32)
    list(APPEND DOMINO_SYS_SOURCES
        plat/dos32/dos32_sys.c
    )
endif()
if(DSYS_BACKEND_WIN16)
    list(APPEND DOMINO_SYS_SOURCES
        plat/win16/win16_sys.c
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
if(DOMINO_USE_COCOA_BACKEND OR DSYS_BACKEND_COCOA)
    list(APPEND DOMINO_SYS_SOURCES
        plat/cocoa/cocoa_sys.c
        plat/cocoa/cocoa_sys_objc.m
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
if(DSYS_BACKEND_DOS16)
    target_compile_definitions(domino_sys PRIVATE DSYS_BACKEND_DOS16)
endif()
if(DSYS_BACKEND_DOS32)
    target_compile_definitions(domino_sys PRIVATE DSYS_BACKEND_DOS32)
endif()
if(DSYS_BACKEND_WIN16)
    target_compile_definitions(domino_sys PRIVATE DSYS_BACKEND_WIN16)
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
if(DOMINO_USE_COCOA_BACKEND OR DSYS_BACKEND_COCOA)
    target_compile_definitions(domino_sys PRIVATE DSYS_BACKEND_COCOA)
    find_library(COCOA_FRAMEWORK Cocoa)
    find_library(APPKIT_FRAMEWORK AppKit)
    find_library(FOUNDATION_FRAMEWORK Foundation)
    if(COCOA_FRAMEWORK)
        target_link_libraries(domino_sys PRIVATE ${COCOA_FRAMEWORK})
    endif()
    if(APPKIT_FRAMEWORK)
        target_link_libraries(domino_sys PRIVATE ${APPKIT_FRAMEWORK})
    endif()
    if(FOUNDATION_FRAMEWORK)
        target_link_libraries(domino_sys PRIVATE ${FOUNDATION_FRAMEWORK})
    endif()
    set_source_files_properties(plat/cocoa/cocoa_sys_objc.m PROPERTIES
        LANGUAGE OBJC
        COMPILE_FLAGS "-fobjc-arc"
    )
endif()
