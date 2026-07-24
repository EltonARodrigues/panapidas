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
from gi.repository import Gtk

from panapidas.widget.map_list_menu import MapListMenu
from panapidas.model.map_entry import MapEntry
from panapidas.request.http_request import request
from panapidas.model.requests import Request

@Gtk.Template(resource_path='/eltonarodrigues/org/codeberg/panapidas/page/request_page.ui')
class RequestPage(Adw.Bin):
    __gtype_name__ = 'RequestPage'

    http_method_list = Gtk.Template.Child()
    method_list = Gtk.Template.Child()
    url_entry = Gtk.Template.Child()
    request_header_list = Gtk.Template.Child()
    request_params_list = Gtk.Template.Child()
    body_type_widget = Gtk.Template.Child()

    def __init__(self, request: Request, **kwargs):
        super().__init__(**kwargs)

        self.request = request

        self.http_method_list.set_selected(self.method_list.find(request.method or "GET"))

        self.url_entry.set_text(request.url or "")

        self.headers = MapListMenu(self.request_header_list, request.headers)
        self.headers.connect("map-changed", self.on_map_change, "headers")

        self.params = MapListMenu(self.request_params_list, request.params)
        self.params.connect("map-changed", self.on_map_change, "params")

        self.request_text_body = Gtk.TextView(
            monospace= True,
            hexpand= True,
            vexpand= True
        )

        buffer = self.request_text_body.get_buffer()
        if type(request.body) == str:
            buffer.set_text(request.body)
        buffer.connect("changed", self.on_request_body_change)

        self.body_params_list = Gtk.ListBox()
        self.body_params_list.set_css_classes(["boxed-list"])

        body_params_filter = request.body if type(request.body) == "list" else []
        self.body_params = MapListMenu(self.body_params_list, body_params_filter)


    @staticmethod
    def get_text_view_value(viewer: Gtk.TextView):
        buffer = viewer.get_buffer()
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        return buffer.get_text(start_iter, end_iter, True)

    @Gtk.Template.Callback()
    def on_send(self, widget):
        print(f"URL: {self.url}")
        print(f"Method: {self.http_method_list.props.selected_item.get_string()}")

        request_body = RequestPage.get_text_view_value(self.response_body)
        print(f"Body: {request_body}")
        print(self.headers.get_map())

        response = request(
            url=self.url,
            data=None,
            params=None,
            headers=self.headers.get_map(),
            method=self.http_method_list.props.selected_item.get_string(),
            data_as_json=True,
            error_count=0
        )

        buffer = self.response_body.get_buffer()
        buffer.set_text(response.body)


    @Gtk.Template.Callback()
    def on_body_type_change(self, widget: Adw.ToggleGroup, active_name: str):
        body_type = widget.get_property(active_name.get_name())

        for child in self.body_type_widget:
            if child.get_name() != "AdwToggleGroup":
                self.body_type_widget.remove(child)

        if body_type == "raw":
            self.body_type_widget.append(self.request_text_body)
        if body_type == "form_data" or body_type == "form_urlencoded":
            self.body_type_widget.append(self.body_params_list)

    @Gtk.Template.Callback()
    def on_method_change(self, widget, _):
        method=widget.props.selected_item.get_string()
        self.request.method = method

    @Gtk.Template.Callback()
    def on_url_change(self, widget):
        self.request.url = widget.get_text()

    def on_map_change(self, widget, type: str):
        values = widget.get_map_entry()

        if type == "params":
            self.request.params = values
        if type == "headers":
            self.request.headers = values

    def on_request_body_change(self, buffer):
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        return buffer.get_text(start_iter, end_iter, True)
        self.request.body = widget.get_text()

