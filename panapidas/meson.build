pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'api_test'
gnome = import('gnome')

blueprints = custom_target('blueprints',
  input: files(
    'window.blp',
    'shortcuts-dialog.blp',
    'page/request_page.blp',
    'page/env_page.blp',
    'page/env_config_page.blp',
    'page/preferences_page.blp',
    'widget/request_sidebar.blp',
    'widget/item_popover.blp',
    'widget/rename_popover.blp',
    'widget/body_source_view.blp',
    'widget/rename_dialog.blp',
  ),
  output: '.',
  command: [
    find_program('blueprint-compiler'),
    'batch-compile',
    '@OUTPUT@',
    '@CURRENT_SOURCE_DIR@',
    '@INPUT@',
  ],
)


gnome.compile_resources('panapidas',
  'panapidas.gresource.xml',
  dependencies: blueprints,
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'panapidas.in',
  output: 'panapidas',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)

install_subdir(
  meson.current_source_dir(),
  exclude_directories: ['.mypy_cache', '__pycache__'],
  exclude_files: ['panapidas.in', 'meson.build'],
  install_dir: python_dir,
)
