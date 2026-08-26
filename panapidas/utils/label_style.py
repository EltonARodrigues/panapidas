import re

from gi.repository import Gtk, Pango

VARIABLE_PATTERN = r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}"


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
