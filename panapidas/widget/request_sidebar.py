from gi.repository import Gtk, Gio, Adw, GObject, GLib, Pango

from panapidas.model.requests import Request, RequestGroup, RequestItem
from panapidas.widget.item_popover import ItemPopover
from panapidas.widget.rename_popover import RenamePopover

RIGHT_MOUSE_BUTTON = 3
LEFT_MOUSE_BUTTON = 1


@Gtk.Template(
    resource_path="/eltonarodrigues/org/codeberg/panapidas/widget/request_sidebar.ui"
)
class RequestSidebar(Adw.NavigationPage):
    __gtype_name__ = "RequestSidebar"

    __gsignals__ = {
        "request-selected": (GObject.SignalFlags.RUN_FIRST, None, (Request,)),
        "save-requests": (GObject.SignalFlags.RUN_FIRST, None, ()),
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

        self.selection = Gtk.SingleSelection.new()
        self.selection.set_autoselect(False)
        self.selection.connect("notify::selected", self.on_selected)
        self.selection.set_model(group_list_model)
        self.request_view.set_model(self.selection)

    @Gtk.Template.Callback()
    def on_setup_factory(
        self, factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem
    ):
        box = Gtk.Box(spacing=6)
        expander = Gtk.TreeExpander()
        expander.set_child(box)

        list_item.set_child(expander)

    @Gtk.Template.Callback()
    def on_bind_factory(
        self, factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem
    ):
        expander = list_item.get_child()
        box = expander.get_child()

        tree_row = list_item.get_item()
        expander.props.list_row = tree_row

        item = tree_row.get_item()

        gesture_right = Gtk.GestureClick()
        gesture_right.set_button(RIGHT_MOUSE_BUTTON)
        gesture_right.connect("pressed", self.on_cell_right_click, expander, item)
        expander.add_controller(gesture_right)

        if not hasattr(item, "children"):
            icon = Gtk.Image.new_from_icon_name("dot-large-symbolic")
            icon.set_visible(False)
            box.append(icon)

            gesture_left = Gtk.GestureClick()
            gesture_left.set_button(LEFT_MOUSE_BUTTON)
            gesture_left.connect(
                "pressed", lambda self, _g, _n, _x, icon: icon.set_visible(True),
                icon
            )
            expander.add_controller(gesture_left)

        method_class = ["method_pill"]
        if hasattr(item, "method") and item.method is not None:
            expander.set_indent_for_icon(False)

            method_class.append(f"method_{item.method.lower()}")

            method_box = Gtk.CenterBox()
            method_box.set_css_classes(method_class)
            method_box.set_center_widget(Gtk.Label(label=item.method))
            box.append(method_box)

        label = Gtk.Label(label=item.name)
        label.set_tooltip_text(item.name)
        label.set_max_width_chars(20)
        label.set_ellipsize(Pango.EllipsizeMode.END)
        box.append(label)

        list_item.changed_handler = item.connect(
            "notify::name", self._on_item_changed, label
        )

    @Gtk.Template.Callback()
    def on_unbind_factory(self, _, list_item: Gtk.ListItem):
        tree_row = list_item.get_item()

        if tree_row is None:
            return

        item = tree_row.get_item()
        handler = getattr(list_item, "changed_handler", None)

        if handler and item:
            item.disconnect(handler)
            list_item.changed_handler = None

    def _on_item_changed(self, item: RequestItem, _, label: Gtk.Label):
        self.on_selected(self.selection, None)
        label.set_text(item.name)
        label.set_tooltip_text(item.name)

    def on_cell_right_click(
        self,
        _gesture: Gtk.GestureClick,
        _n_press: int,
        _x: float,
        _y: float,
        expander: Gtk.TreeExpander,
        item: RequestItem,
    ):
        self.target_item = item
        self.actual_popover_position = expander
        self.popover.create_menu_model(item)
        self.popover.unparent()
        self.popover.set_parent(self.actual_popover_position)
        self.popover.show()

    def on_rename(self, _widget: Gtk.Button, _target: GLib.Variant):
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
            return

        self.emit("request-selected", item)
