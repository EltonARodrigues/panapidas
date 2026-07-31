from gi.repository import Gtk, Gio, GObject, GLib

from panapidas.model.requests import RequestItem


@Gtk.Template(
    resource_path="/eltonarodrigues/org/codeberg/panapidas/widget/item_popover.ui"
)
class ItemPopover(Gtk.PopoverMenu):
    __gtype_name__ = "ItemPopover"

    def __init__(self):
        super().__init__()

        self.set_position(Gtk.PositionType.RIGHT)

    def create_menu_model(self, item: RequestItem):
        menu = Gio.Menu()

        item_type = GObject.type_name(item.__gtype__)

        if item_type == "RequestGroup":
            new_item_section = Gio.Menu()
            new_folder = Gio.MenuItem.new("New Folder")
            new_folder.set_action_and_target_value(
                "app.create-sub-folder", GLib.Variant.new_string(item.id)
            )
            new_item_section.append_item(new_folder)

            new_request = Gio.MenuItem.new("New Request")
            new_request.set_action_and_target_value(
                "app.create-sub-request", GLib.Variant.new_string(item.id)
            )
            new_item_section.append_item(new_request)

            menu.append_section(None, new_item_section)

        section = Gio.Menu()

        rename = Gio.MenuItem.new("Rename")
        rename.set_action_and_target_value(
            "sidebar.rename-item", GLib.Variant.new_string(item.id)
        )

        section.append_item(rename)

        delete = Gio.MenuItem.new("Delete")
        delete.set_action_and_target_value(
            "app.delete-item", GLib.Variant.new_string(item.id)
        )

        section.append_item(delete)

        menu.append_section(None, section)

        self.set_menu_model(menu)
