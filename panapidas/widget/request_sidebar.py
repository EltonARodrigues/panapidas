import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject, Gdk, GLib

from panapidas.model.requests import Request, RequestGroup, RequestItem
from panapidas.widget.item_popover import ItemPopover
from panapidas.widget.rename_popover import RenamePopover

RIGHT_MOUSE_BUTTON = 3

@Gtk.Template(
    resource_path="/eltonarodrigues/org/codeberg/panapidas/widget/request_sidebar.ui"
)
class RequestSidebar(Adw.NavigationPage):
    __gtype_name__ = "RequestSidebar"

    __gsignals__ = {
        'request-selected': (GObject.SignalFlags.RUN_FIRST, None, (Request,)),
        'save-requests': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    request_view = Gtk.Template.Child()

    def __init__(self, group_list_model: Gtk.TreeListModel):
        super().__init__()

        self.action_group = Gio.SimpleActionGroup()
        self.insert_action_group("sidebar", self.action_group)

        rename_action = Gio.SimpleAction.new(
            "rename-item",
            GLib.VariantType.new("s"),
        )
        rename_action.connect("activate", self.on_rename)
        self.action_group.add_action(rename_action)

        self.popover = ItemPopover()
        self.rename_popover = RenamePopover()

        self.target_item = None

        self.selection = Gtk.SingleSelection.new(group_list_model)
        self.selection.connect("notify::selected", self.on_selected)
        self.request_view.set_model(self.selection)

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

        gesture.set_button(RIGHT_MOUSE_BUTTON)
        gesture.connect("pressed", self.on_cell_right_click, expander, item)
        expander.add_controller(gesture)

        label.set_text(item.name)

    def on_cell_right_click(self, gesture, n_press, x, y, expander, item: RequestItem):
        self.target_item = item
        self.actual_popover_position = expander
        self.popover.create_menu_model(item)
        self.popover.unparent()
        self.popover.set_parent(self.actual_popover_position)
        self.popover.show()

    def on_rename(self, widget, target):
         self.rename_popover.unparent()
         self.rename_popover.set_rename_item(self.target_item)
         self.rename_popover.set_parent(self.actual_popover_position)
         self.rename_popover.show()

    def on_selected(self, selection: Gtk.SingleSelection, _):
        selected = selection.get_selected_item()

        if not selected:
            return None

        item = selected.get_item()
        item_type = GObject.type_name(item.__gtype__)

        if item_type == "RequestGroup":
            return;

        self.emit('request-selected', item)

