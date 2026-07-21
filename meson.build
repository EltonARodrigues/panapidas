project('panapidas',
          version: '0.1.0',
    meson_version: '>= 1.0.0',
  default_options: [ 'warning_level=2', 'werror=false', ],
)

i18n = import('i18n')
python = import('python')
gnome = import('gnome')

python_bin = python.find_installation(
  'python3',
  modules: [],
)


python_dir = python_bin.get_install_dir()


subdir('data')
subdir('panapidas')
subdir('po')

gnome.post_install(
     glib_compile_schemas: true,
    gtk_update_icon_cache: true,
  update_desktop_database: true,
)
