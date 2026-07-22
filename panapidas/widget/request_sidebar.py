import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GObject
from panapidas.model.requests import RequestGroup


@Gtk.Template(
    resource_path="/eltonarodrigues/org/codeberg/panapidas/widget/request_sidebar.ui"
)
class RequestSidebar(Adw.NavigationPage):
    __gtype_name__ = "RequestSidebar"

    request_view = Gtk.Template.Child()

    def __init__(self, groups: RequestGroup):
        super().__init__()

        root_store = Gio.ListStore.new(RequestGroup)
        root_store.append(groups)

        tree_model = Gtk.TreeListModel.new(
            root_store, False, True, RequestSidebar.create_model_func
        )

        self.selection = Gtk.SingleSelection.new(tree_model)
        self.request_view.set_model(self.selection)

    @staticmethod
    def create_model_func(item):
        """Retorna um ListStore com os filhos ou None."""
        item_type = GObject.type_name(item.__gtype__)

        if not item or item_type == "Request":
            return None

        store = Gio.ListStore.new(GObject.GObject)

        if (item_type == "RequestGroup"):
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
        label.set_text(item.name)


