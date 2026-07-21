# window.py
#
# Copyright 2026 Elton de Andrade Rodrigues
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw
from gi.repository import Gtk, GObject, Gio
from panapidas.widget.map_list_menu import MapListMenu


@Gtk.Template(resource_path='/eltonarodrigues/org/codeberg/restest/window.ui')
class ApiTestWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'ApiTestWindow'

    http_method_list = Gtk.Template.Child()
    request_header_list = Gtk.Template.Child()
    request_params_list = Gtk.Template.Child()
    request_body = Gtk.Template.Child()


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.url = ""
        self.headers = MapListMenu(self.request_header_list)
        self.params = MapListMenu(self.request_params_list)


    @Gtk.Template.Callback()
    def on_send(self, widget):
        print(f"URL: {self.url}")
        print(f"Method: {self.http_method_list.props.selected_item.get_string()}")
        print(f"Body {self.request_body}")
        print(self.headers.get_map())


    @Gtk.Template.Callback()
    def on_url_change(self, entry: Gtk.Entry):
        self.url = entry.get_text()

