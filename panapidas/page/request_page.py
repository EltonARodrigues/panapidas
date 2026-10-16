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

from gi.repository import Adw, GLib, Gtk, GObject, Pango

from panapidas.model import env_object
from panapidas.widget.map_list_menu import MapListMenu
from panapidas.widget.body_source_view import BodySourceView
from panapidas.request.http_request import request, Response
from panapidas.model.env_object import ActiveEnvs, EnvObject
from panapidas.model.requests import Request
from panapidas.utils.entry_env_formatter import (
    apply_env,
    apply_env_style,
    entry_env_change_gesture,
)
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
    body_toggle_type = Gtk.Template.Child()
    body_type_request = Gtk.Template.Child()
    response_body = Gtk.Template.Child()
    default_status_bar_label = Gtk.Template.Child()
    request_info_toggle_group = Gtk.Template.Child()
    response_status_label = Gtk.Template.Child()
    response_time_label = Gtk.Template.Child()
    response_size_label = Gtk.Template.Child()
    script_type_toggle_group = Gtk.Template.Child()
    script_source_view = Gtk.Template.Child()
    response_header_list = Gtk.Template.Child()

    def __init__(self, request: Request, **kwargs):
        super().__init__(**kwargs)

        self.request = request

        entry_env_change_gesture(self.url_entry)

        self.activeEnv = ActiveEnvs()
        self.activeEnv.connect("env-changed", self.on_change_env)
        self.envs = self.activeEnv.dict_envs

        self.connect("destroy", self._on_page_destroy)

        self.active_request = False
        self.is_destroyed = False
        self.stop_event = threading.Event()

        body_type = request.body["type"]

        self.request_body_source = BodySourceView()
        request_body_buffer = self.request_body_source.get_buffer()
        request_body_buffer.set_text(request.body["raw"] if body_type == "raw" else "")

        request_body_buffer.connect("changed", self._get_source_view_text)

        self.body_params_list = Gtk.ListBox(selection_mode=0)
        self.body_params_list.set_css_classes(["custom_list"])

        self.script_source_view.set_language("js")

        self.script_buffer = self.script_source_view.get_buffer()
        self.script_buffer.connect("changed", self._on_script_buffer_changed)

        self.script_runner = ScriptRequest(self.request, self.activeEnv)

        self._load_request(self.request)

    def _load_request(self, request: Request):
        method = request.method or "GET"
        self.http_method_list.set_selected(self.method_list.find(method))
        self.http_method_list.set_css_classes(["toggle", f"method_{method.lower()}"])

        self.url_entry.set_text(request.url or "")

        self.headers = MapListMenu(
            self.request_header_list, request.headers, self.envs, True
        )
        self.headers.connect("map-changed", self._on_map_change, "headers")

        self.params = MapListMenu(
            self.request_params_list, request.params, self.envs, True
        )
        self.params.connect("map-changed", self._on_map_change, "params")

        self.body_toggle_type.set_active_name(request.body["type"] or "None")

        self.request_body_source.set_hexpand(True)
        self.request_body_source.set_halign(Gtk.Align.FILL)
        self.request_body_source.set_size_request(-1, 500)

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

        self.request_info_toggle_group.set_visible(True)
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

        self.script_runner.run(self.scripts["pos_script"], response=response)

        self.response_header_list.remove_all()
        for header in response.headers.items():
            row = MapListMenu.on_ready_only_list_row(header[0], header[1])
            self.response_header_list.append(row)

        return False

    def _get_source_view_text(self, buffer) -> str:
        body = self.request.body
        body["type"] = "raw"
        body["raw"] = buffer.get_text(
            buffer.get_start_iter(), buffer.get_end_iter(), False
        )
        self.request.body = body


    def _call_request(self):
        response = request(
            url=apply_env(self.envs, self.url_entry.get_text()),
            body=Request.convert_body_to_dict(self.request.body, apply_env),
            params=self.params.get_formated_dict(),
            headers=self.headers.get_formated_dict() or {},
            method=self.http_method_list.props.selected_item.get_string(),
            data_as_json=self.request.body["type"] == "raw",
            body_type=self.request.body["type"],
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

        if type in ["form_data", "urlencoded"]:
            body = self.request.body
            body[type] = values
            body["type"] = type
            self.request.body = body

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
    def on_body_type_change(
        self, widget: Adw.ToggleGroup, active_name: GObject.ParamSpec
    ):
        body_type = widget.get_property(active_name.get_name())

        body = self.request.body
        body["type"] = body_type
        self.request.body = body

        if body_type == "none":
            self.body_type_request.set_child(None)

        if body_type == "raw":
            request_body_buffer = self.request_body_source.get_buffer()
            request_body_buffer.set_text(self.request.body["raw"])
            self.body_type_request.set_child(self.request_body_source)

        if body_type in ["form_data", "urlencoded"]:
            body_params_filter = (
                self.request.body[body_type]
                if body_type in ["form_data", "urlencoded"]
                else []
            )
            MapListMenu(
                self.body_params_list, body_params_filter, self.envs, True
            ).connect("map-changed", self._on_map_change, body_type)
            self.body_type_request.set_child(self.body_params_list)

    @Gtk.Template.Callback()
    def on_script_type_change(
        self, widget: Adw.ToggleGroup, active_name: GObject.ParamSpec
    ):
        script_type = widget.get_property(active_name.get_name())
        self.script_buffer.set_text(
            (
                self.scripts["pre_script"]
                if (script_type == "pre")
                else self.scripts["pos_script"]
            ),
            -1,
        )

    @Gtk.Template.Callback()
    def on_request_info_change(
        self, widget: Adw.ToggleGroup, active_name: GObject.ParamSpec
    ):
        toggle_name = widget.get_property(active_name.get_name())

        if (toggle_name == "body"):
            self.response_header_list.set_visible(False)
            self.response_body.set_visible(True)

        if (toggle_name == "headers"):
            self.response_header_list.set_visible(True)
            self.response_body.set_visible(False)


    @Gtk.Template.Callback()
    def on_method_change(self, widget: Gtk.DropDown, _):
        method = widget.props.selected_item.get_string()
        if self.request.method != method:
            widget.set_css_classes(["toggle", f"method_{method.lower()}"])
        self.request.method = method

    @Gtk.Template.Callback()
    def on_url_change(self, widget: Gtk.Entry):
        text = widget.get_text()
        self.request.url = text

        apply_env_style(self.envs, text, widget)
