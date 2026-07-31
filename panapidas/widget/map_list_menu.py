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

from gi.repository import Adw, Gtk, GObject, Gio

from panapidas.model.map_entry import MapEntry


class MapListMenu(GObject.Object):
    __gtype_name__ = "MapListMenu"

    __gsignals__ = {"map-changed": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ())}

    def __init__(self, list_box: Gtk.ListBox, items: list[MapEntry] = []):
        super().__init__()

        self.list_box = list_box
        self.items = items.copy()
        self.items.append(MapEntry(id=len(self.items) + 1, key="", value=""))

        self.list_model = Gio.ListStore(item_type=MapEntry)
        self.list_model.splice(0, 0, additions=self.items)

        self.list_box.bind_model(self.list_model, self._on_create_list_row)

    def _on_destroy_row(self, event_name: str, row_id: int):
        row_count = self.list_model.get_n_items()

        for index in range(row_count):
            item = self.list_model.get_item(index)

            if index + 1 == row_count:
                return False

            if item.id == row_id:
                self.list_model.remove(index)
                return True

        self._on_map_change()

    def _on_map_change(self):
        self.emit("map-changed")

    def _on_entry_changed(
        self, entry: GObject.Object, entry_type: str, list_model: GObject.Object
    ):
        new_id = list_model.id + 1
        has_row = [model for model in self.list_model if model.id == new_id]

        if not has_row:
            self.list_model.append(MapEntry(id=new_id, key="", value=""))

        text_value = entry.get_text()

        if entry_type == "key":
            list_model.key = text_value

        if entry_type == "value":
            list_model.value = text_value

        self._on_map_change()

    def _on_create_list_row(self, model: MapEntry):
        linked_box = Gtk.Box(
            margin_top=8,
            margin_start=8,
            margin_end=8,
            margin_bottom=8,
            halign="fill",
            orientation="horizontal",
        )
        linked_box.set_css_classes(["linked"])

        key_entry = Gtk.Entry(hexpand=True, placeholder_text="Key", text=model.key)
        key_entry.connect("changed", self._on_entry_changed, "key", model)

        value_entry = Gtk.Entry(
            hexpand=True, placeholder_text="Value", text=model.value
        )
        value_entry.connect("changed", self._on_entry_changed, "value", model)

        close_button = Gtk.Button(
            icon_name="edit-delete-symbolic",
            tooltip_text="Remover item",
            halign="center",
            valign="center",
        )

        close_button.connect("clicked", self._on_destroy_row, model.id)

        linked_box.append(key_entry)
        linked_box.append(value_entry)
        linked_box.append(close_button)

        self.list_box.append(linked_box)

    def get_map_entry(self):
        return [row for row in self.list_model if len(row.key) > 0]

    def get_dict(self):
        items_dict = {row.key: row.value for row in self.list_model if len(row.key) > 0}
        return items_dict if len(items_dict.keys()) > 0 else None
