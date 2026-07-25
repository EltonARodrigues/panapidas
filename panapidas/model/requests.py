import uuid

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import GObject, Gio

from panapidas.model.map_entry import MapEntry


class RequestItem(GObject.GObject):
    __gtype_name__ = "RequestItem"

class Request(RequestItem):
    __gtype_name__ = "Request"

    def __init__(
        self,
        id: str = None,
        name: str = None,
        method: str = None,
        url: str = None,
        headers: MapEntry = [],
        body = None,
        params: MapEntry = [],
    ):
        super().__init__()
        self._id = str(uuid.uuid4()) if id is None else id,
        self.name = name
        self.url = url
        self.method = method
        self.headers = headers
        self.params = params
        self.body = body

    @GObject.Property(type=str)
    def id(self):
        return self._id[0]

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "method": self.method,
            "headers": [header.to_dict() for header in self.headers],
            "params": [param.to_dict() for param in self.params],
            "body": self.body,
        }


class RequestGroup(RequestItem):
    __gtype_name__ = "RequestGroup"

    def __init__(self, id= None, name=None, children_list=[]):

        super().__init__()
        self.id = str(uuid.uuid4()) if id is None else id
        self.name = name
        self.children = RequestGroup._children_builder(children_list)

    @staticmethod
    def _build_map_entry(map_list: list):
        return [
            MapEntry(
                id=row["id"],
                key=row["key"],
                value=row["value"],
            )
            for row in map_list
        ]

    @staticmethod
    def _children_builder(children_list=[]):
        children_store = Gio.ListStore.new(RequestItem)
        for children in children_list:
            if "children" in children:
                children_store.append(
                    RequestGroup(id=children["id"], name=children["name"], children_list=children["children"])
                )
                continue

            children_store.append(
                Request(
                    id=children["id"],
                    name=children["name"],
                    url=children["url"],
                    method=children["method"],
                    headers=RequestGroup._build_map_entry(children["headers"]),
                    params=RequestGroup._build_map_entry(children["params"]),
                    body=children["body"],
                )
            )

        return children_store

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "children": [children.to_dict() for children in self.children],
        }

