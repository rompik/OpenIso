# Configure main script with paths
configure_file(
  input: 'openiso.in',
  output: 'openiso',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)

# Install Python module (main folder and subfolders)
moduledir = join_paths(py_installation.get_install_dir(), 'openiso')

# Install files recursively
install_subdir('controller', install_dir: moduledir)
install_subdir('core', install_dir: moduledir)
install_subdir('model', install_dir: moduledir)
install_subdir('view', install_dir: moduledir)

# Main module files
python_sources = [
  '__init__.py',
  '__main__.py',
  'application.py',
]

install_data(python_sources, install_dir: moduledir)
