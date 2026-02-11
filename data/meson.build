# Desktop file
desktop_file = i18n.merge_file(
  input: 'io.github.rompik.OpenIso.desktop.in',
  output: 'io.github.rompik.OpenIso.desktop',
  type: 'desktop',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications')
)

# Desktop file validation
desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils, args: [desktop_file])
endif

# AppStream metainfo
metainfo_file = i18n.merge_file(
  input: 'io.github.rompik.OpenIso.metainfo.xml.in',
  output: 'io.github.rompik.OpenIso.metainfo.xml',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'metainfo')
)

# Metainfo validation
appstreamcli = find_program('appstreamcli', required: false)
if appstreamcli.found()
  test('Validate appstream file', appstreamcli,
    args: ['validate', '--no-net', '--explain', metainfo_file])
endif

# GSettings schema
install_data(
  'io.github.rompik.OpenIso.gschema.xml',
  install_dir: join_paths(get_option('datadir'), 'glib-2.0', 'schemas')
)

# Compile GSettings schemas for development
compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Compile GSettings schemas', compile_schemas,
    args: ['--strict', '--dry-run', meson.current_source_dir()])
endif

# Icons
subdir('icons')

# Application data files
install_subdir(
  'settings',
  install_dir: join_paths(get_option('datadir'), meson.project_name())
)

install_subdir(
  'database',
  install_dir: join_paths(get_option('datadir'), meson.project_name())
)
