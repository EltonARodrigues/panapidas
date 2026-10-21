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

from gi.repository import Adw, Gio, Gtk, GObject

from panapidas.model.env_object import EnvObject, ActiveEnvs
from panapidas.widget.request_sidebar import RequestSidebar
from panapidas.page.request_page import RequestPage
from panapidas.page.env_page import EnvPage
from panapidas.page.env_config_page import EnvConfigPage
from panapidas.model.requests import Request


@Gtk.Template(resource_path="/eltonarodrigues/org/codeberg/panapidas/window.ui")
class PanapidasWindow(Adw.ApplicationWindow):
    __gtype_name__ = "PanapidasWindow"

    __gsignals__ = {"save-signal": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (str,))}

    split_view = Gtk.Template.Child()
    page_navigation_view = Gtk.Template.Child()
    env_group_dropdown = Gtk.Template.Child()
    request_layout = Gtk.Template.Child()
    env_config_layout = Gtk.Template.Child()
    content_request = Gtk.Template.Child()
    request_navigation = Gtk.Template.Child()
    save_request_button = Gtk.Template.Child()
    toast_overlay_status = Gtk.Template.Child()

    def __init__(self, group_list_model: Gtk.TreeListModel, envs_store: Gio.ListStore, **kwargs):
        super().__init__(**kwargs)

        self.env_selected = None
        self.request_selected = None
        self.request_id_selected = None

        self.env_group_dropdown.set_expression(
            Gtk.ClosureExpression.new(
                GObject.TYPE_STRING,
                lambda item: item.name if item else "",
                [],
            )
        )

        self.activeEnv = ActiveEnvs()

        self.env_group_dropdown.set_model(Gtk.SingleSelection.new(envs_store))


        self.env_layout = EnvPage(env_store=envs_store)
        self.env_layout.connect("env-selected", self._on_env_selected)
        self.env_layout.connect("env-saved", self.on_save, 'env')

        self.env_config_layout.connect("env-saved", self.on_save, 'env')

        self.request_pages = {}
        self.save_request_button.set_visible(False)

        group_list_model.connect("items-changed", self._on_list_model_change)

        sidebar = RequestSidebar(group_list_model)
        self.split_view.set_sidebar(sidebar)
        sidebar.connect("request-selected", self.on_request_selected)

        action = Gio.SimpleAction.new('env_page', None)
        action.connect('activate', self._on_open_envs)

        self.add_action(action)
    
    def _on_open_envs(self, _action: Gio.SimpleAction, _target):
        self.page_navigation_view.push(self.env_layout)

    @Gtk.Template.Callback()
    def on_env_group_selected(self, dropdown: Gtk.DropDown, _: GObject):
        env_group = dropdown.get_selected_item()

        if env_group:
            self.activeEnv.initialize(env_group.id, env_group.name, env_group.envs)
            self.env_selected = env_group;

            if self.request_selected:
                self.request_selected.on_change_env(self.env_selected)

    @Gtk.Template.Callback()
    def on_save(self, _, type: str = "request"):
        self.emit("save-signal", type)

    def show_toast(self, msg: str):
        toast = Adw.Toast.new(msg)
        toast.set_timeout(2)
        self.toast_overlay_status.add_toast(toast)

    def _on_env_selected(self, widget: EnvPage, env_object):
        self.env_config_layout.set_env(env_object)
        self.page_navigation_view.push(self.env_config_layout)

    def on_request_selected(self, sidebar: RequestSidebar, request: Request):
        if request.id not in self.request_pages:
            self.request_pages[request.id] = RequestPage(request)

        self.request_navigation.set_title(request.name)
        self.save_request_button.set_visible(True)
        self.request_selected = self.request_pages[request.id]
        self.request_id_selected = request.id
        self.content_request.set_content(self.request_pages[request.id])

    def _on_list_model_change(
        self, list_model: Gtk.TreeListModel, position: int, removed: int, added: int
    ):
        if removed > 0:
            actual_ids = [item.get_item().id for item in list_model]

            pages_ids = self.request_pages.keys()
            removed_ids = list(set(pages_ids).difference(actual_ids))

            for request_id in removed_ids:
                self.request_pages.pop(request_id, None)

                if request_id == self.request_id_selected:
                    self.content_request.set_content(None)
