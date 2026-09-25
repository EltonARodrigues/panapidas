import json

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

        self.client_cert_list: list[dict] = [];
        self._load_client_cert_list()

    def _save_client_cert_list(self, certificate: dict):
        print(f"Saving certificate: {certificate}")
        self.client_cert_list.append(certificate)
        self.settings.set_string("client-certificates", json.dumps(self.client_cert_list))

    def _load_client_cert_list(self):
        raw = self.settings.get_string("client-certificates")
        self.client_cert_list = json.loads(raw)

        print(f"Loading client certificates: {self.client_cert_list}")
        for cert in self.client_cert_list:
            self._add_cert_row(cert)

    def _delete_cert(self, button: Gtk.Button, row: Adw.ExpanderRow):
        print(f"Deleting certificate for URL: {row.get_title()}")
        self.client_cert_list = [cert for cert in self.client_cert_list if cert["url"] != row.get_title()]
        self.settings.set_string("client-certificates", json.dumps(self.client_cert_list))

        self.cert_list_box.remove(row)

    def _add_cert_row(self, certificate: dict) -> Adw.ExpanderRow:
        row = Adw.ExpanderRow(title=certificate["url"])

        delete_cert_button = Gtk.Button(
            label="Delete Certificate",
            icon_name="user-trash-symbolic",
            halign="center",
            valign="center",
        )
        delete_cert_button.connect("clicked", self._delete_cert, row)

        row.add_suffix(delete_cert_button)

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
        cert = widget.get_certificate()
        self._add_cert_row(cert)
        self._save_client_cert_list(cert)


    @Gtk.Template.Callback()
    def on_add_certificate(self, button):
        certificate_dialog = AddCertificateDialog()
        certificate_dialog.connect("response", self._save_cert)
        certificate_dialog.present(self)
