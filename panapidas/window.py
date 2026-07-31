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

import os
import json

from gi.repository import Adw, Gtk, GObject

from panapidas.widget.request_sidebar import RequestSidebar
from panapidas.page.request_page import RequestPage
from panapidas.model.requests import Request


@Gtk.Template(resource_path="/eltonarodrigues/org/codeberg/panapidas/window.ui")
class PalapidasWindow(Adw.ApplicationWindow):
    __gtype_name__ = "PalapidasWindow"

    __gsignals__ = {"save-requests": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ())}

    split_view = Gtk.Template.Child()
    content_request = Gtk.Template.Child()
    request_navigation = Gtk.Template.Child()
    save_request_button = Gtk.Template.Child()

    def __init__(self, group_list_model: Gtk.TreeListModel, **kwargs):
        super().__init__(**kwargs)

        self.request_pages = {}
        self.save_request_button.set_visible(False)

        group_list_model.connect("items-changed", self._on_list_model_change)

        sidebar = RequestSidebar(group_list_model)
        self.split_view.set_sidebar(sidebar)
        sidebar.connect("request-selected", self.on_request_selected)

    def on_request_selected(self, sidebar: RequestSidebar, request: Request):
        if request.id not in self.request_pages:
            self.request_pages[request.id] = RequestPage(request)

        self.request_navigation.set_title(request.name)
        self.save_request_button.set_visible(True)
        self.content_request.set_content(self.request_pages[request.id])

    @Gtk.Template.Callback()
    def on_request_save(self, _):
        self.emit("save-requests")

    def _on_list_model_change(
        self, list_model: Gtk.TreeListModel, position: int, removed: int, added: int
    ):
        if removed > 0:
            actual_ids = [item.get_item().id for item in list_model]

            pages_ids = self.request_pages.keys()
            removed_ids = list(set(pages_ids).difference(actual_ids))

            for k in removed_ids:
                self.request_pages.pop(k, None)

            self.content_request.set_content(None)
