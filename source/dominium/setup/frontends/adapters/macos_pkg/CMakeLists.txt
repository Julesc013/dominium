cmake_minimum_required(VERSION 3.16)

if(APPLE)
    enable_language(OBJC)

    set(DSK_MACOS_GUI_ROOT ${CMAKE_CURRENT_LIST_DIR}/xcode/DominiumSetupMacApp)
    set(DSK_MACOS_GUI_SOURCES
        ${DSK_MACOS_GUI_ROOT}/Sources/main.m
        ${DSK_MACOS_GUI_ROOT}/Sources/AppDelegate.m
        ${DSK_MACOS_GUI_ROOT}/Sources/DominiumSetupViewController.m
    )
    set(DSK_MACOS_GUI_RESOURCES
        ${DSK_MACOS_GUI_ROOT}/Resources/Base.lproj/Main.storyboard
        ${DSK_MACOS_GUI_ROOT}/Resources/Assets.xcassets
    )

    add_executable(dominium-setup-macos-gui MACOSX_BUNDLE
        ${DSK_MACOS_GUI_SOURCES}
        ${DSK_MACOS_GUI_RESOURCES}
    )
    set_source_files_properties(
        ${DSK_MACOS_GUI_ROOT}/Resources/Base.lproj/Main.storyboard
        PROPERTIES MACOSX_PACKAGE_LOCATION "Resources/Base.lproj"
    )
    set_source_files_properties(
        ${DSK_MACOS_GUI_ROOT}/Resources/Assets.xcassets
        PROPERTIES MACOSX_PACKAGE_LOCATION "Resources"
    )
    target_link_libraries(dominium-setup-macos-gui
        PRIVATE
            "-framework Cocoa"
            "-framework AppKit"
            "-framework Foundation"
    )
    target_compile_options(dominium-setup-macos-gui PRIVATE
        "-fobjc-arc"
    )
    set_target_properties(dominium-setup-macos-gui PROPERTIES
        OUTPUT_NAME "dominium-setup-macos-gui"
        MACOSX_BUNDLE_INFO_PLIST "${DSK_MACOS_GUI_ROOT}/Resources/Info.plist"
    )

    add_custom_target(build-macos-gui-adapter
        DEPENDS dominium-setup-macos-gui
    )

    add_custom_target(build-macos-pkg-wrapper
        COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_CURRENT_BINARY_DIR}/packaging
        COMMAND ${CMAKE_COMMAND} -E copy_directory
            ${CMAKE_CURRENT_SOURCE_DIR}/packaging
            ${CMAKE_CURRENT_BINARY_DIR}/packaging
        COMMENT "Staging setup macOS PKG wrapper scripts"
    )
else()
    add_custom_target(build-macos-pkg-wrapper)
endif()
