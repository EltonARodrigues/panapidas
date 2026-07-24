import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject
from panapidas.model.requests import Request, RequestGroup


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

        tree_model = Gtk.TreeListModel.new(
            store, False, True, RequestSidebar.create_model_func
        )

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
        print(item_type)
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
        item = tree_row.get_item()
        # item.connect("click", self.teste)
        label.set_text(item.name)

    def on_selected(self, selection: Gtk.SingleSelection, _):
        selected = selection.get_selected_item()
        item = selected.get_item()
        item_type = GObject.type_name(item.__gtype__)

        if item_type == "RequestGroup":
            return;

        self.emit('request-selected', item)

