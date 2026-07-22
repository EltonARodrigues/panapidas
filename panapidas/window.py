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
from panapidas.widget.request_sidebar import RequestSidebar
from panapidas.page.request_page import RequestPage
from panapidas.request.http_request import request
from panapidas.model.requests import Request, RequestGroup

class TreeNode(GObject.Object):
    def __init__(self, _title, _children=None):
        super().__init__()
        self.children = _children or []
        # self.title = _title
        self.item = Gtk.ListBoxRow().set_child(Gtk.Label(label=_title))

    @GObject.Property(type=Gtk.ListBoxRow)
    def item(self):
        return self.item


@Gtk.Template(resource_path='/eltonarodrigues/org/codeberg/panapidas/window.ui')
class PalapidasWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'PalapidasWindow'

    split_view = Gtk.Template.Child()
    content_request = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root_model = RequestGroup(
            "Root",
            [
                RequestGroup("Collection 1", [Request("GET - test"), Request("POST - abc")]),
                RequestGroup(
                    "Collection 2",
                    [
                        Request("DELETE - afsfs"),
                        Request("PATCH - ffff"),
                        RequestGroup("Folder 1", [Request("GET - 1234")]),
                    ],
                ),
            ]
        )

        request_list = RequestSidebar(root_model)
        self.split_view.set_sidebar(request_list)

        request_page = RequestPage()
        self.content_request.set_content(request_page)

