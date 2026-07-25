# main.py
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

import sys
import gi
import os
import json

from gettext import gettext as _

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Gio, Adw, GLib, GObject

from panapidas.model.requests import Request, RequestGroup, RequestItem
from panapidas.data_management import DataManagement
from .window import PalapidasWindow

APPLICATION_NAME = "panapidas"
APPLICATION_DATA_FILENAME = "requests.json"


class PalapidasApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(
            application_id="eltonarodrigues.org.codeberg.palapidas",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
            resource_base_path="/eltonarodrigues/org/codeberg/panapidas",
        )
        self.dataManagement = DataManagement()
        self.request_group = self.dataManagement.load()

        self.cache_por_id = {}

        self.request_group_store = Gio.ListStore.new(RequestItem)
        self.request_group_store.splice(0,0,additions=self.request_group.children)
        self.group_list_model = Gtk.TreeListModel.new(self.request_group_store, False, True, self.create_child_model)

        self.create_action("quit", lambda *_: self.quit(), None, ["<control>q"])
        self.create_action("about", self.on_about_action)
        self.create_action("preferences", self.on_preferences_action)
        self.create_action("create_folder", self.on_create)
        self.create_action("create_request", self.on_create)
        self.create_action("create-sub-folder", self.on_create, GLib.VariantType.new("s"))
        self.create_action("create-sub-request", self.on_create, GLib.VariantType.new("s"))
        self.create_action("delete-item", self.on_create, GLib.VariantType.new("s"))

    def create_child_model(self, item):
        item_type = GObject.type_name(item.__gtype__)
        if item_type == "RequestGroup":
            return item.children

    def on_save_request(self, _):
        self.dataManagement.save(self.request_group)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """

        win = self.props.active_window
        if not win:
            win = PalapidasWindow(application=self, group_list_model=self.group_list_model)
            win.connect("save-requests", self.on_save_request)
        win.present()

    def on_about_action(self, *args):
        """Callback for the app.about action."""
        about = Adw.AboutDialog(
            application_name=APPLICATION_NAME,
            application_icon="eltonarodrigues.org.codeberg.palapidas",
            developer_name="Elton de Andrade Rodrigues",
            version="0.1.0",
            # Translators: Replace "translator-credits" with your name/username, and optionally an email or URL.
            translator_credits=_("translator-credits"),
            developers=["Elton de Andrade Rodrigues"],
            copyright="© 2026 Elton de Andrade Rodrigues",
        )
        about.present(self.props.active_window)

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        print("app.preferences action activated")

    def on_create(self, action: Gio.SimpleAction, target):
        action_name = action.get_name()

        if action_name == "create-sub-folder":
            parent_item_id = target.unpack()
            DataManagement.add_item(
                item= self.request_group_store[0],
                id= parent_item_id,
                new_item= RequestGroup(name = "New Folder")
            )

        if action_name == "delete-item":
            parent_item_id = target.unpack()
            DataManagement.remove_by_id(self.request_group_store, parent_item_id)

        if action_name == "create-sub-request":
            parent_item_id = target.unpack()
            DataManagement.add_item(
                item= self.request_group_store[0],
                id= parent_item_id,
                new_item= Request(name = "New Request")
            )
            print(self.request_group)


        if action_name == "create_folder":
            new_group = RequestGroup(name= "New Group")
            self.request_group.children.append(new_group)
            self.request_group_store.append(new_group)

        if action_name == "create_request":
            new_request = Request(name= "New Request")
            self.request_group.children.append(new_request)
            self.request_group_store.append(new_request)

        self.dataManagement.save(self.request_group)

    def create_action(self, name, callback, target=None, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """

        action = Gio.SimpleAction.new(name, target)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    """The application's entry point."""
    app = PalapidasApplication()
    return app.run(sys.argv)

