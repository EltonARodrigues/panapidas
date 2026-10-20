import base64
import uuid

from gi.repository import Gio, GObject

from panapidas.model.map_entry import MapEntry
from panapidas.model.env_object import ActiveEnvs


class RequestItem(GObject.GObject):
    __gtype_name__ = "RequestItem"

    def __init__(self, name_atr: str = None):
        super().__init__()
        self._name = name_atr
        self._changed_handler = None

    @GObject.Property(type=str)
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @GObject.Property(type=str)
    def changed_handler(self) -> str:
        return self._changed_handler

    @changed_handler.setter
    def changed_handler(self, value: str):
        self._changed_handler = value


class Request(RequestItem):
    __gtype_name__ = "Request"

    def __init__(
        self,
        id: str = None,
        name: str = None,
        method: str = None,
        url: str = None,
        headers: MapEntry = None,
        body=None,
        params: MapEntry = None,
        scripts: dict[str, str] = None,
    ):
        super().__init__(name_atr=name)
        self._id = str(uuid.uuid4()) if id is None else id
        self.url = url
        self.method = method or "GET"
        self.headers = headers or []
        self.params = params or []

        if body is None:
            self._body = {
                "type": None,
                "raw": "",
                "form_data": [],
                "urlencoded": [],
            }
        else:
            self._body = {
                "type": body["type"],
                "raw": body["raw"],
                "form_data": Request.map_builder(body["form_data"]),
                "urlencoded": Request.map_builder(body["urlencoded"]),
            }

        self._scripts = scripts or {"pre_script": "", "pos_script": ""}

    @staticmethod
    def map_builder(entry_list):

        if isinstance(entry_list, dict):
            return [
                MapEntry(id=index, key=form[0], value=form[1])
                for index, form in enumerate(entry_list.items())
            ]

        return [
            MapEntry(
                id=index, key=form["key"], value=form["value"], active=form["active"]
            )
            for index, form in enumerate(entry_list)
        ]

    @GObject.Property(type=str)
    def id(self) -> str:
        return self._id[0]

    @GObject.Property()
    def scripts(self) -> dict:
        return Request.base64_to_script(self._scripts)

    @scripts.setter
    def scripts(self, value: dict):
        self._scripts = Request.script_to_base64(value)

    @GObject.Property()
    def body(self) -> dict:
        return self._body

    @body.setter
    def body(self, body: dict):
        self._body = body

    def to_dict(self) -> dict[str, any]:
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "method": self.method,
            "headers": [header.to_dict() for header in self.headers],
            "params": [param.to_dict() for param in self.params],
            "body": Request.convert_body_to_dict(self._body),
            "scripts": self._scripts,
        }

    @staticmethod
    def convert_body_to_dict(body: dict, apply_env=None, filter_active=False):
        if apply_env is not None:
            envs = ActiveEnvs().dict_envs

            return {
                "type": body["type"],
                "form_data": {
                    apply_env(envs, row.key): apply_env(envs, row.value)
                    for row in body["form_data"]
                    if not (filter_active and not row.active)
                },
                "urlencoded": {
                    apply_env(envs, row.key): apply_env(envs, row.value)
                    for row in body["urlencoded"]
                    if not (filter_active and not row.active)
                },
                "raw": body["raw"],
            }

        return {
            "type": body["type"],
            "form_data": {
                row.key: row.value
                for row in body["form_data"]
                if not (filter_active and not row.active)
            },
            "urlencoded": {
                row.key: row.value
                for row in body["urlencoded"]
                if not (filter_active and not row.active)
            },
            "raw": body["raw"],
        }

    @staticmethod
    def script_to_base64(script_dict: dict[str, str]) -> dict[str, str]:
        return {
            "pre_script": base64.b64encode(
                script_dict["pre_script"].encode("utf-8")
            ).decode("utf-8"),
            "pos_script": base64.b64encode(
                script_dict["pos_script"].encode("utf-8")
            ).decode("utf-8"),
        }

    @staticmethod
    def base64_to_script(script_dict: dict[str, str]) -> dict[str, str]:
        return {
            "pre_script": base64.b64decode(script_dict["pre_script"]).decode("utf-8"),
            "pos_script": base64.b64decode(script_dict["pos_script"]).decode("utf-8"),
        }


class RequestGroup(RequestItem):
    __gtype_name__ = "RequestGroup"

    def __init__(self, id=None, name=None, children_list=[]):

        super().__init__(name_atr=name)
        self.id = str(uuid.uuid4()) if id is None else id
        self.children = RequestGroup.children_builder(children_list)

    @staticmethod
    def build_map_entry(map_list: list) -> list[MapEntry]:
        return [
            MapEntry(
                id=row["id"], key=row["key"], value=row["value"], active=row["active"]
            )
            for row in map_list
        ]

    @staticmethod
    def children_builder(children_list=[]) -> Gio.ListStore:
        children_store = Gio.ListStore.new(RequestItem)
        for children in children_list:
            if "children" in children:
                children_store.append(
                    RequestGroup(
                        id=children["id"],
                        name=children["name"],
                        children_list=children["children"],
                    )
                )
                continue

            children_store.append(
                Request(
                    id=children["id"],
                    name=children["name"],
                    url=children["url"],
                    method=children["method"],
                    headers=RequestGroup.build_map_entry(children["headers"]),
                    params=RequestGroup.build_map_entry(children["params"]),
                    body=children["body"],
                    scripts=children["scripts"],
                )
            )

        return children_store

    def to_dict(self) -> dict[str, any]:
        return {
            "id": self.id,
            "name": self.name,
            "children": [children.to_dict() for children in self.children],
        }
