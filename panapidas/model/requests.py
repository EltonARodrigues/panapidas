import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GObject

from panapidas.model.map_entry import MapEntry


class Request(GObject.GObject):
    __gtype_name__ = "Request"

    def __init__(
        self,
        name: str,
        method: str,
        url: str,
        headers: MapEntry,
        body,
        params: MapEntry,
    ):
        super().__init__()
        self.name = name
        self.url = url
        self.method = method
        self.headers = headers
        self.params = params
        self.body = body

    def to_dict(self):
        return {
            "name": self.name,
            "url": self.url,
            "method": self.method,
            "headers": [header.to_dict() for header in self.headers],
            "params": [param.to_dict() for param in self.params],
            "body": self.body,
        }


class RequestGroup(GObject.GObject):
    __gtype_name__ = "RequestGroup"

    def __init__(self, name, children_list=[]):

        super().__init__()
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
        children_object = []
        for children in children_list:
            if "children" in children:
                children_object.append(
                    RequestGroup(children["name"], children["children"])
                )
                continue
            children_object.append(
                Request(
                    name=children["name"],
                    url=children["url"],
                    method=children["method"],
                    headers=RequestGroup._build_map_entry(children["headers"]),
                    params=RequestGroup._build_map_entry(children["params"]),
                    body=children["body"],
                )
            )

        return children_object

    def to_dict(self):
        return {
            "name": self.name,
            "children": [children.to_dict() for children in self.children],
        }

