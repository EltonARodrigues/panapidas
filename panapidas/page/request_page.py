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

from gi.repository import Gtk, Adw

from panapidas.widget.map_list_menu import MapListMenu
from panapidas.widget.body_source_view import BodySourceView
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
    body_type_request = Gtk.Template.Child()
    response_body = Gtk.Template.Child()
    default_status_bar_label = Gtk.Template.Child()
    response_status_label = Gtk.Template.Child()
    response_time_label = Gtk.Template.Child()
    response_size_label = Gtk.Template.Child()

    def __init__(self, request: Request, **kwargs):
        super().__init__(**kwargs)

        self.request = request

        self.http_method_list.set_selected(self.method_list.find(request.method or "GET"))

        self.url_entry.set_text(request.url or "")

        self.headers = MapListMenu(self.request_header_list, request.headers)
        self.headers.connect("map-changed", self.on_map_change, "headers")

        self.params = MapListMenu(self.request_params_list, request.params)
        self.params.connect("map-changed", self.on_map_change, "params")

        self.body_params_list = Gtk.ListBox(selection_mode=0)

        body_params_filter = request.body if type(request.body) == "list" else []
        self.body_params = MapListMenu(self.body_params_list, body_params_filter)

        body_params_filter = request.body if type(request.body) == "list" else []

        self.requestBodySourceView = BodySourceView()
        self.requestBodySourceView.set_hexpand(True)
        self.requestBodySourceView.set_halign(Gtk.Align.FILL)
        self.requestBodySourceView.set_size_request(-1, 500)

        self.body_type=None

    @staticmethod
    def set_response_bar_label(label: Gtk.Label, text: str):
        label_template_text = label.get_text()
        label.set_visible(True)
        label.set_text(label_template_text.format(text))

    @Gtk.Template.Callback()
    def on_send(self, widget):
        buffer = self.requestBodySourceView.get_buffer()
        body_str = buffer.get_text(
            buffer.get_start_iter(),
            buffer.get_end_iter(),
            False
        )

        response = request(
            url=self.url_entry.get_text(),
            body=body_str,
            params=self.body_params.get_dict(),
            headers=self.headers.get_dict() or {},
            method=self.http_method_list.props.selected_item.get_string(),
            data_as_json= self.body_type == "raw" ,
            body_type=self.body_type
        )

        self.default_status_bar_label.set_visible(False)

        RequestPage.set_response_bar_label(self.response_status_label, response.status)
        RequestPage.set_response_bar_label(self.response_time_label, response.time_seconds)
        RequestPage.set_response_bar_label(self.response_size_label, response.response_size)

        buffer = self.response_body.get_buffer()
        buffer.set_text(response.body, -1)


    @Gtk.Template.Callback()
    def on_body_type_change(self, widget: Adw.ToggleGroup, active_name: str):
        self.body_type = widget.get_property(active_name.get_name())

        if self.body_type == "none":
            self.body_type_request.set_child(None)

        if self.body_type == "raw":
            self.body_type_request.set_child(self.requestBodySourceView)
        if self.body_type in ["form_data", "form_urlencoded"]:
            self.body_type_request.set_child(self.body_params_list)

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

