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
from src.model.header import Header


@Gtk.Template(resource_path='/eltonarodrigues/org/codeberg/restest/window.ui')
class ApiTestWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'ApiTestWindow'

    header_list = Gtk.Template.Child()
    request_header_list = Gtk.Template.Child()


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.header_model = Gio.ListStore(item_type=Header)
        self.header_model.append(Header(id=1, key="", value=""))
        self.request_header_list.bind_model(self.header_model, self.create_header_row);

    def destroy_header_row(self, event_name: str, header_id: int):
        header_count = self.header_model.get_n_items()

        for index in range(header_count):
            item = self.header_model.get_item(index)
            if(index + 1 == header_count):
                print(f"Item com ID {header_id} INGNORADO!")
                return False

            if item.id == header_id:
                self.header_model.remove(index)
                print(f"Item com ID {header_id} removido com sucesso!")
                return True

    def handler_headers(self, entry: GObject.Object, entry_type: str, header_model: GObject.Object):
        new_id = header_model.id + 1
        has_row = [header for header in self.header_model if header.id == new_id]

        if not has_row:
            self.header_model.append(Header(id=new_id, key="", value=""))

        print(entry)
        text_value = entry.get_text()
        if entry_type == "key":
            header_model.key = text_value
        if entry_type == "value":
            header_model.value = text_value

    def create_header_row(self, model):
        header_box = Gtk.Box(
            margin_top= 8,
            margin_start= 8,
            margin_end= 8,
            margin_bottom= 8,
            halign="fill",
            orientation="horizontal",
        )
        header_box.set_css_classes(["linked"])

        key_entry = Gtk.Entry(
            hexpand=True,
            placeholder_text="Key",
        )
        key_entry.connect("changed", self.handler_headers, "key", model)

        value_entry = Gtk.Entry(
            hexpand=True,
            placeholder_text="Value"
        )

        value_entry.connect("changed", self.handler_headers, "value", model)


        close_button = Gtk.Button(
            icon_name="edit-delete-symbolic",
            tooltip_text="Remover item",
            halign="center",
            valign="center"
        )

        close_button.connect("clicked", self.destroy_header_row, model.id)

        header_box.append(key_entry)
        header_box.append(value_entry)
        header_box.append(close_button)

        self.request_header_list.append(header_box)

    @Gtk.Template.Callback()
    def on_changed(self, widget):

        widget_name = widget.get_buildable_id()


        if widget_name == 'url_entry':
            text = widget.get_text()
            print(f"Live text: {text}")
            return

