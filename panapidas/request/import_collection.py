import json
import uuid
from typing import Union

from urllib.parse import parse_qsl, urlencode, urlunparse, urlparse

from panapidas.model.requests import Request, RequestGroup, RequestItem
from panapidas.model.map_entry import MapEntry


class ImportCollection:

    @staticmethod
    def convert_object(items):
        if isinstance(items, list):
            return [
                {"id": index, "key": item["key"], "value": item["value"]}
                for index, item in enumerate(items)
            ]
        return []

    @staticmethod
    def split_url_params(url_string: str):
        parsed = urlparse(url_string)
        url = urlunparse(parsed._replace(query=""))

        params_extract = parse_qsl(parsed.query, keep_blank_values=True)
        params = [
            {"id": i, "key": p[0], "value": p[1]} for i, p in enumerate(params_extract)
        ]
        return url, params

    @staticmethod
    def url_object_to_string(url_obj: dict) -> str | list:
        if isinstance(url_obj, str):
            return ImportCollection.split_url_params(url_obj)

        if "raw" in url_obj:
            return ImportCollection.split_url_params(url_obj["raw"])

        protocol = url_obj.get("protocol", "")
        protocol_part = f"{protocol}://" if protocol else ""

        host = url_obj.get("host", [])
        if isinstance(host, str):
            host = host.split(".")
        host_part = ".".join(host)

        path = url_obj.get("path", [])
        if isinstance(path, str):
            path = path.split("/")
        path_resolved = []
        path_part = "/" + "/".join(path_resolved) if path_resolved else ""

        query: list = url_obj.get("query", [])

        hash_part = url_obj.get("hash", "")
        hash_part = f"#{hash_part}" if hash_part else ""

        url: str = f"{protocol_part}{host_part}{path_part}{hash_part}"
        return url, query

    def convert_postman_item(self, item: dict):
        if "item" in item:
            return {
                "id": str(uuid.uuid4()),
                "name": item["name"],
                "children": self.convert_group(item["item"]),
            }

        url, params = (
            ImportCollection.url_object_to_string(item["request"])
            if isinstance(item["request"], str)
            else ImportCollection.url_object_to_string(item["request"]["url"])
        )

        body = {
            "type": None,
            "raw": None,
            "form_data": {},
            "urlencoded": {},
        }

        if "body" in item["request"]:
            body_type = item["request"]["body"]["mode"]

            body["type"] = item["request"]["body"]["mode"]
            body["raw"] = item["request"]["body"]["raw"] if body_type == "raw" else ""
            body["form_data"] = item["request"]["body"]["form_data"] if body_type == "form_data" else {}
            body["urlencoded"] = item["request"]["body"]["urlencoded"] if body_type == "urlencoded" else {}

        return {
            "id": str(uuid.uuid4()),
            "name": item["name"],
            "method": (
                "GET"
                if isinstance(item["request"], str) or "method" not in item["request"]
                else item["request"]["method"]
            ),
            "url": url,
            "headers": (
                ImportCollection.convert_object(item["request"]["header"])
                if "header" in item["request"]
                else []
            ),
            "params": params,
            "body": body,
            "scripts": {"pre_script": "", "pos_script": ""},
        }

    def convert_group(self, items):
        return [self.convert_postman_item(item) for item in items]

    def postman_collection(self, filepath: str):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        children = self.convert_group(data["item"])

        collection = RequestGroup(name=data["info"]["name"], children_list=children)
        return collection
