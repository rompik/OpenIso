### CMakeLists automatically created with AutoVala
### Do not edit

set (DATADIR "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_DATAROOTDIR}")
set (PKGDATADIR "${DATADIR}/openiso")
set (GETTEXT_PACKAGE "openiso")
set (RELEASE_NAME "openiso")
set (CMAKE_C_FLAGS "")
set (PREFIX ${CMAKE_INSTALL_PREFIX})
set (VERSION "1.0.0")
set (TESTSRCDIR "${CMAKE_SOURCE_DIR}")
set (DOLLAR "$")

configure_file (${CMAKE_SOURCE_DIR}/src/Config.vala.cmake ${CMAKE_BINARY_DIR}/src/Config.vala)
add_definitions(-DGETTEXT_PACKAGE=\"${GETTEXT_PACKAGE}\")
set (VERSION "1.0.0")
add_definitions (${DEPS_CFLAGS})
link_libraries ( ${DEPS_LIBRARIES} )
link_directories ( ${DEPS_LIBRARY_DIRS} )
find_package (Vala REQUIRED)
include (ValaVersion)
ensure_vala_version ("0.32" MINIMUM)
include (ValaPrecompile)

set (VALA_PACKAGES ${VALA_PACKAGES} atk)
set (VALA_PACKAGES ${VALA_PACKAGES} cairo)
set (VALA_PACKAGES ${VALA_PACKAGES} gdk-3.0)
set (VALA_PACKAGES ${VALA_PACKAGES} gdk-pixbuf-2.0)
set (VALA_PACKAGES ${VALA_PACKAGES} gio-2.0)
set (VALA_PACKAGES ${VALA_PACKAGES} glib-2.0)
set (VALA_PACKAGES ${VALA_PACKAGES} gobject-2.0)
set (VALA_PACKAGES ${VALA_PACKAGES} gtk+-3.0)
set (VALA_PACKAGES ${VALA_PACKAGES} pango)
set (VALA_PACKAGES ${VALA_PACKAGES} pangocairo)
set (VALA_PACKAGES ${VALA_PACKAGES} x11)

set (APP_SOURCES ${APP_SOURCES} ${CMAKE_CURRENT_BINARY_DIR}/Config.vala)
set (APP_SOURCES ${APP_SOURCES} core/connections/openiso.core.connections.point.vala)
set (APP_SOURCES ${APP_SOURCES} core/drawing/openiso.core.drawing.note.atext.vala)
set (APP_SOURCES ${APP_SOURCES} core/drawing/openiso.core.drawing.note.text.vala)
set (APP_SOURCES ${APP_SOURCES} core/drawing/openiso.core.drawing.shape.line.vala)
set (APP_SOURCES ${APP_SOURCES} core/drawing/openiso.core.drawing.shape.rectangle.vala)
set (APP_SOURCES ${APP_SOURCES} core/drawing/openiso.core.drawing.sheet.vala)
set (APP_SOURCES ${APP_SOURCES} core/drawing/openiso.core.drawing.skey.vala)
set (APP_SOURCES ${APP_SOURCES} core/errors/openiso.core.errors.vala)
set (APP_SOURCES ${APP_SOURCES} core/export/openiso.core.export.svg.vala)
set (APP_SOURCES ${APP_SOURCES} core/import/openiso.core.import.idf.vala)
set (APP_SOURCES ${APP_SOURCES} core/import/openiso.core.import.xml.vala)
set (APP_SOURCES ${APP_SOURCES} core/mto/openiso.core.mto.material.vala)
set (APP_SOURCES ${APP_SOURCES} core/piping/openiso.core.piping.component.vala)
set (APP_SOURCES ${APP_SOURCES} core/piping/openiso.core.piping.pipe.vala)
set (APP_SOURCES ${APP_SOURCES} core/revisions/openiso.core.revisions.revision.vala)
set (APP_SOURCES ${APP_SOURCES} openiso.application.vala)
set (APP_SOURCES ${APP_SOURCES} openiso.test.pipes.vala)
set (APP_SOURCES ${APP_SOURCES} openiso.vala)
set (APP_SOURCES ${APP_SOURCES} ui/openiso.ui.windows.main.vala)


if ((${CMAKE_BUILD_TYPE} STREQUAL "Debug") OR (${CMAKE_BUILD_TYPE} STREQUAL "RelWithDebInfo"))
	set(COMPILE_OPTIONS ${COMPILE_OPTIONS} "-g")
endif()

vala_precompile(VALA_C openiso
	${APP_SOURCES}
PACKAGES
	${VALA_PACKAGES}
)

add_executable(openiso ${VALA_C})
target_link_libraries( openiso m )


install(TARGETS
	openiso
RUNTIME DESTINATION
	${CMAKE_INSTALL_BINDIR}
)
if(HAVE_VALADOC)
	valadoc(openiso
		${CMAKE_BINARY_DIR}/valadoc/openiso
		${APP_SOURCES}
	PACKAGES
		${VALA_PACKAGES}
	CUSTOM_VAPIS
		${CUSTOM_VAPIS_LIST}
	)
	install(DIRECTORY
		${CMAKE_BINARY_DIR}/valadoc
	DESTINATION
		${CMAKE_INSTALL_DATAROOTDIR}/doc/openiso
	)
endif()
