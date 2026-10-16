from email.mime import text
from os import name
import re

from gi.repository import Gtk, Pango

from panapidas.model.env_object import ActiveEnvs
from panapidas.widget.change_value_dialog import ChangeValueDialog


VARIABLE_PATTERN = r"\{\{\s*([A-Za-z_][A-Za-z0-9_-]*)\s*\}\}"


def _create_pango_attr(match: re.match):
    start = match.start()
    end = match.end()

    color = Pango.Color()
    color.parse("orange")

    bg_attr = Pango.attr_foreground_new(color.red, color.green, color.blue)
    bg_attr.start_index = start
    bg_attr.end_index = end

    return bg_attr


def apply_env(envs: dict, text: str):
    formated_text = text

    for match in re.finditer(VARIABLE_PATTERN, text):
        var_name = match.group(1)
        var_value = next(
            (d.get("value") for d in envs if d.get("key") == var_name), None
        )

        if var_value:
            formated_text = formated_text.replace(match.group(), var_value or var_name)

    return formated_text


def apply_env_style(envs: dict, text: str, entry: Gtk.Entry):
    attr_list = Pango.AttrList()

    var_pattern = re.search(VARIABLE_PATTERN, text)
    if not var_pattern:
        return None

    formated_text = text
    
    for match in re.finditer(VARIABLE_PATTERN, text):
        var_name = match.group(1)
        var_value = next(
            (d.get("value") for d in envs if d.get("key") == var_name), None
        )

        if var_value:
            formated_text = formated_text.replace(match.group(), var_value or var_name)
        attr_list.insert(_create_pango_attr(match))

    entry.set_attributes(attr_list)
    entry.set_tooltip_text(formated_text)

def find_match_at(text, index) -> str | None:
    for match in re.finditer(VARIABLE_PATTERN, text):
        start, end = match.span(1)
        if start <= index < end:
            return match.group(1)
    return None


def entry_env_change_gesture(entry: Gtk.Entry):
    gesture = Gtk.GestureClick.new()
    gesture.connect("pressed", on_entry_clicked, entry)
    entry.get_first_child().add_controller(gesture)

def on_entry_clicked(gesture, n_press, x, y, entry):
    text = entry.get_text()
    pango_context = entry.get_pango_context()

    layout = Pango.Layout(pango_context)
    layout.set_text(text, -1)
    
    x_pango = int(x * Pango.SCALE)
    y_pango = int(y * Pango.SCALE)
    
    _, index, _ = Pango.Layout.xy_to_index(
        layout, x_pango, y_pango
    )

    env_key = find_match_at(text, index)

    if(env_key):
        _on_change_env_key(env_key, entry.get_root())

def _on_change_env_key(key: str, root_widget: Gtk.Widget = None):
    active_env = ActiveEnvs()
    env_value_dialog = ChangeValueDialog(
        value=active_env.get_env(key),
        heading=f"Environment Variable: {key}",
        body=None,
    )
    env_value_dialog.connect("response", _on_env_value_changed, active_env, key)
    env_value_dialog.present(root_widget)

def _on_env_value_changed(widget: ChangeValueDialog, response_name: str, active_env: ActiveEnvs, key: str):
    if response_name != "save":
        return

    active_env.set_env(key, widget.get_value())

    window = widget.get_root()
    window.emit("save-signal", "env")
