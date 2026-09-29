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

import threading

from gi.repository import Adw, GLib, Gtk, GObject

from panapidas.widget.map_list_menu import MapListMenu
from panapidas.widget.body_source_view import BodySourceView
from panapidas.request.http_request import request, Response
from panapidas.model.env_object import EnvObject
from panapidas.model.requests import Request
from panapidas.utils.label_style import apply_env, apply_env_style
from panapidas.request.script_request import ScriptRequest


@Gtk.Template(
    resource_path="/eltonarodrigues/org/codeberg/panapidas/page/request_page.ui"
)
class RequestPage(Adw.Bin):
    __gtype_name__ = "RequestPage"

    http_method_list = Gtk.Template.Child()
    method_list = Gtk.Template.Child()
    url_entry = Gtk.Template.Child()
    send_request_button = Gtk.Template.Child()
    cancel_request_button = Gtk.Template.Child()
    request_header_list = Gtk.Template.Child()
    request_params_list = Gtk.Template.Child()
    body_type_request = Gtk.Template.Child()
    response_body = Gtk.Template.Child()
    default_status_bar_label = Gtk.Template.Child()
    response_status_label = Gtk.Template.Child()
    response_time_label = Gtk.Template.Child()
    response_size_label = Gtk.Template.Child()
    script_type_toggle_group = Gtk.Template.Child()
    script_source_view = Gtk.Template.Child()

    def __init__(self, env_object: EnvObject, request: Request, **kwargs):
        super().__init__(**kwargs)

        self.request = request
        self.envs = env_object.dict_envs

        self.connect("destroy", self._on_page_destroy)

        self.active_request = False
        self.is_destroyed = False
        self.stop_event = threading.Event()

        self.body_type = None

        self.script_source_view.set_language("js")

        self.script_buffer = self.script_source_view.get_buffer()
        self.script_buffer.connect("changed", self._on_script_buffer_changed)

        self.script_runner = ScriptRequest(None, None, self.envs)

        self._load_request(request)


    def _load_request(self, request: Request):
        self.http_method_list.set_selected(
            self.method_list.find(request.method or "GET")
        )

        self.url_entry.set_text(request.url or "")

        self.headers = MapListMenu(self.request_header_list, request.headers, self.envs)
        self.headers.connect("map-changed", self._on_map_change, "headers")

        self.params = MapListMenu(self.request_params_list, request.params, self.envs)
        self.params.connect("map-changed", self._on_map_change, "params")

        self.body_params_list = Gtk.ListBox(selection_mode=0)

        body_params_filter = request.body if type(request.body) == "list" else []
        self.body_params = MapListMenu(
            self.body_params_list, body_params_filter, self.envs
        )

        self.requestBodySourceView = BodySourceView()
        self.requestBodySourceView.set_hexpand(True)
        self.requestBodySourceView.set_halign(Gtk.Align.FILL)
        self.requestBodySourceView.set_size_request(-1, 500)

        self.scripts = request.scripts
        self.script_buffer.set_text(self.scripts["pre_script"])
        

    @staticmethod
    def set_response_bar_label(label: Gtk.Label, text: str):
        label_template_text = label.get_text()
        label.set_visible(True)
        label.set_text(label_template_text.format(text))

    def on_change_env(self, env_group: EnvObject):
        self.envs = env_group.dict_envs
        self._load_request(self.request)

    def _render_response(self, response: Response) -> bool:
        self.default_status_bar_label.set_visible(False)

        self.send_request_button.set_visible(True)
        self.cancel_request_button.set_visible(False)

        RequestPage.set_response_bar_label(self.response_status_label, response.status)
        RequestPage.set_response_bar_label(
            self.response_time_label, response.time_seconds
        )
        RequestPage.set_response_bar_label(
            self.response_size_label, response.response_size
        )

        buffer = self.response_body.get_buffer()
        buffer.set_text(response.body, -1)

        self.script_runner.run(self.scripts["pos_script"])

        return False

    def _get_source_view_text(self, source_view: BodySourceView) -> str:
        buffer = source_view.get_buffer()
        return buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)

    def _call_request(self):
        body = (
            self._get_source_view_text(self.requestBodySourceView)
            if self.body_type == "raw"
            else None
        )
        response = request(
            url=apply_env(self.envs, self.url_entry.get_text()),
            body=body,
            params=self.body_params.get_formated_dict(),
            headers=self.headers.get_formated_dict() or {},
            method=self.http_method_list.props.selected_item.get_string(),
            data_as_json=self.body_type == "raw",
            body_type=self.body_type,
        )

        if self.stop_event.is_set():
            return

        GLib.idle_add(self._render_response, response)
        self.active_request = False

    def _on_map_change(self, widget: MapListMenu, type: str):
        values = widget.get_map_entry()

        if type == "params":
            self.request.params = values

        if type == "headers":
            self.request.headers = values

    def _on_page_destroy(self):
        self.is_destroyed = True

        if self.active_request:
            self.stop_event.set()
            self.active_request = False

    def _on_script_buffer_changed(self, buffer: Gtk.TextBuffer):
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)

        if self.script_type_toggle_group.get_active_name() == "pre":
            self.scripts["pre_script"] = text
        else:
            self.scripts["pos_script"] = text

        self.request.scripts = self.scripts

    @Gtk.Template.Callback()
    def on_send(self, _):
        self.script_runner.run(self.scripts["pre_script"])
        if self.is_destroyed or self.active_request:
            return None

        self.stop_event.clear()
        self.active_request = True
        self.send_request_button.set_visible(False)
        self.cancel_request_button.set_visible(True)

        self.worker_thread = threading.Thread(target=self._call_request, daemon=True)
        self.worker_thread.start()

    @Gtk.Template.Callback()
    def on_cancel(self, _):
        if self.active_request and not self.is_destroyed:
            self.send_request_button.set_visible(True)
            self.cancel_request_button.set_visible(False)
            self.stop_event.set()
            self.active_request = False

    @Gtk.Template.Callback()
    def on_body_type_change(self, widget: Adw.ToggleGroup, active_name: GObject.ParamSpec):
        self.body_type = widget.get_property(active_name.get_name())

        if self.body_type == "none":
            self.body_type_request.set_child(None)

        if self.body_type == "raw":
            self.body_type_request.set_child(self.requestBodySourceView)

        if self.body_type in ["form_data", "form_urlencoded"]:
            self.body_type_request.set_child(self.body_params_list)

    @Gtk.Template.Callback()
    def on_script_type_change(self, widget: Adw.ToggleGroup, active_name: GObject.ParamSpec):
        script_type = widget.get_property(active_name.get_name())
        self.script_buffer.set_text(
            self.scripts["pre_script"] if (script_type == "pre") else self.scripts["pos_script"],
            -1,
        )

    @Gtk.Template.Callback()
    def on_method_change(self, widget: Gtk.DropDown, _):
        method = widget.props.selected_item.get_string()
        self.request.method = method

    @Gtk.Template.Callback()
    def on_url_change(self, widget: Gtk.Entry):
        text = widget.get_text()
        self.request.url = text

        apply_env_style(self.envs, text, widget)
