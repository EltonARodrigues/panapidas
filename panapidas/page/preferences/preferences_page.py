from gi.repository import Adw, Gtk, Gio

from panapidas.widget.add_certificate import AddCertificateDialog
from panapidas.widget.map_list_menu import MapListMenu
from panapidas.model.env_object import EnvObject


@Gtk.Template(
    resource_path="/eltonarodrigues/org/codeberg/panapidas/page/preferences/preferences_page.ui"
)
class PreferencesPage(Adw.PreferencesDialog):
    __gtype_name__ = "PreferencesPage"

    request_timeout_row = Gtk.Template.Child()
    cert_list_box = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings.new("eltonarodrigues.org.codeberg.panapidas")

        self.settings.bind(
            "general-request-timeout",
            self.request_timeout_row,
            "value",
            Gio.SettingsBindFlags.DEFAULT
        )

    def _add_cert_row(self, certificate: dict) -> Adw.ExpanderRow:
        row = Adw.ExpanderRow(title=certificate["url"])
        row.add_suffix(
            Gtk.Button(
                label="Delete Certificate",
                icon_name="user-trash-symbolic",
                halign="center",
                valign="center",
            )
        )

        if certificate["crt"]:
            row.add_row(Adw.ActionRow(title=certificate["crt"]))
        if certificate["key"]:
            row.add_row(Adw.ActionRow(title=certificate["key"]))
        if certificate["pfx"]:
            row.add_row(Adw.ActionRow(title=certificate["pfx"]))

        self.cert_list_box.append(row)

    def _save_cert(self, widget: Gtk.AlertDialog, response_name: str):
        if response_name != "save":
            return
        self._add_cert_row(widget.get_certificate())

    @Gtk.Template.Callback()
    def on_add_certificate(self, button):
        certificate_dialog = AddCertificateDialog()
        certificate_dialog.connect("response", self._save_cert)
        certificate_dialog.present(self)
