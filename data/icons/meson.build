# Install application icon
install_data(
  'logo.svg',
  rename: 'io.github.rompik.OpenIso.svg',
  install_dir: join_paths(get_option('datadir'), 'icons', 'hicolor', 'scalable', 'apps')
)

# Install application-specific icons
install_subdir(
  'common',
  install_dir: join_paths(get_option('datadir'), meson.project_name(), 'icons')
)

install_subdir(
  'primitives',
  install_dir: join_paths(get_option('datadir'), meson.project_name(), 'icons')
)

install_subdir(
  'spindles',
  install_dir: join_paths(get_option('datadir'), meson.project_name(), 'icons')
)
