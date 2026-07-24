import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject, Gdk, GLib

from panapidas.model.requests import Request, RequestGroup
from panapidas.widget.item_popover import ItemPopover

RIGHT_MOUSE_BUTTON = 3

@Gtk.Template(
    resource_path="/eltonarodrigues/org/codeberg/panapidas/widget/request_sidebar.ui"
)
class RequestSidebar(Adw.NavigationPage):
    __gtype_name__ = "RequestSidebar"

    __gsignals__ = {
        'request-selected': (GObject.SignalFlags.RUN_FIRST, None, (Request,)),
    }

    request_view = Gtk.Template.Child()

    def __init__(self, store: Gio.ListStore):
        super().__init__()

        self.store = store
        tree_model = Gtk.TreeListModel.new(
            store, False, True, RequestSidebar.create_model_func
        )

        self.popover = ItemPopover()

        self.selection = Gtk.SingleSelection.new(tree_model)
        self.selection.connect("notify::selected", self.on_selected)
        self.request_view.set_model(self.selection)

    @staticmethod
    def create_model_func(item):
        """Retorna um ListStore com os filhos ou None."""
        item_type = GObject.type_name(item.__gtype__)

        if not item or item_type == "Request":
            return None

        store = Gio.ListStore.new(GObject.GObject)

        if item_type == "RequestGroup":
            for child in item.children:
                child_type = GObject.type_name(item.__gtype__)
                store.append(child)
        return store

    @Gtk.Template.Callback()
    def setup_factory(self, factory, list_item):
        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)

        expander = Gtk.TreeExpander()
        expander.set_child(label)

        list_item.set_child(expander)

    @Gtk.Template.Callback()
    def bind_factory(self, factory, list_item):
        expander = list_item.get_child()
        label = expander.get_child()

        tree_row = list_item.get_item()
        expander.props.list_row = tree_row

        gesture = Gtk.GestureClick()

        item = tree_row.get_item()
        print(item)
        gesture.set_button(RIGHT_MOUSE_BUTTON)
        gesture.connect("pressed", self.on_cell_right_click, expander, item.id)
        expander.add_controller(gesture)

        label.set_text(item.name)

    def on_cell_right_click(self, gesture, n_press, x, y, expander, request_item_id):
        self.create_menu_model(request_item_id)

        self.popover.unparent()
        self.popover.set_parent(expander)
        self.popover.show()

    def create_menu_model(self, request_item_id):
        menu = Gio.Menu()
        section = Gio.Menu()

        new_folder = Gio.MenuItem.new("New Folder")
        new_folder.set_action_and_target_value("app.create-sub-folder", GLib.Variant.new_string(request_item_id))
        section.append_item(new_folder)

        new_request = Gio.MenuItem.new("New Request")
        new_request.set_action_and_target_value("app.create-sub-request", GLib.Variant.new_string(request_item_id))
        section.append_item(new_request)

        rename = Gio.MenuItem.new("Rename")
        rename.set_action_and_target_value("app.delete-item", GLib.Variant.new_string(request_item_id))
        section.append_item(rename)

        delete = Gio.MenuItem.new("Delete")
        delete.set_action_and_target_value("app.delete-item", GLib.Variant.new_string(request_item_id))
        section.append_item(delete)

        menu.append_section(None, section)
        self.popover.set_menu_model(menu)

    def on_selected(self, selection: Gtk.SingleSelection, _):
        selected = selection.get_selected_item()
        item = selected.get_item()
        item_type = GObject.type_name(item.__gtype__)

        if item_type == "RequestGroup":
            return;

        self.emit('request-selected', item)

