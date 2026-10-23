import os
import json
import uuid

from gi.repository import GLib, GObject, Gio

from panapidas.model.requests import RequestGroup, RequestItem
from panapidas.model.env_object import EnvObject

APPLICATION_NAME = "panapidas"
APPLICATION_DATA_FILENAME = "requests.json"
APPLICATION_ENVS_FILENAME = "envs.json"


class DataManagement:

    def __init__(self):
        self.data_dir = GLib.get_user_data_dir()
        self.data_path = os.path.join(self.data_dir, APPLICATION_DATA_FILENAME)
        self.env_path = os.path.join(self.data_dir, APPLICATION_ENVS_FILENAME)
        print(self.data_path)
        self._request_group = None

    @staticmethod
    def create_request_example():
        return {
            "id": "a",
            "name": "Example Request",
            "url": "{{base_url}}/test/post",
            "method": "POST",
            "headers": [
                {
                "id": 0,
                "key": "Content-Type",
                "value": "application/json",
                "active": True
                }
            ],
            "params": [
                {
                "id": 1,
                "key": "foo",
                "value": "bar",
                "active": True
                },
                {
                "id": 2,
                "key": "var",
                "value": "{{var}}",
                "active": True
                }
            ],
            "body": {
                "type": "raw",
                "form_data": {},
                "urlencoded": {},
                "raw": "{\n  \"name\": \"Test\",\n  \"value\": 123\n}"
            },
            "scripts": {
                "pre_script": "dXJsID0gcGEucmVxdWVzdC51cmwKcGEudmFyaWFibGUuc2V0KCJ2YXIiLCB1cmwp",
                "pos_script": "Ym9keSA9IHBhLnJlcXVlc3QuYm9keQpwYS52YXJpYWJsZS5zZXQoImJvZHkiLCBib2R5KQ=="
            }
        }

    def create_root_group(self) -> dict:
        group = {
            "id": str(uuid.uuid4()),
            "name": "Panapidas",
            "children": [DataManagement.create_request_example()],
        }

        with open(self.data_path, "x", encoding="utf-8") as f:
            json.dump(group, f, indent=2, ensure_ascii=False)

        return group

    def _load(self, path: str) -> dict | None:
        if not os.path.exists(path):
            print("Arquivo não encontrado. Retornando lista vazia.")
            return None

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_requests(self) -> RequestGroup:
        data = self._load(self.data_path)

        if not data:
            data = self.create_root_group()

        self._request_group = RequestGroup(data["id"], data["name"], data["children"])
        return self._request_group

    def load_envs(self) -> list[EnvObject]:
        data = self._load(self.env_path)

        if not data:
            return []

        env_list = [
            EnvObject(env["id"], env["name"], env["envs_map"]) for env in data["envs"]
        ]
        return env_list

    def save_envs(self, envs_store):

        envs = []
        for i in range(envs_store.get_n_items()):
            objeto = envs_store.get_item(i)
            envs.append(objeto.to_dict())

        env_dict = {"envs": envs}
        with open(self.env_path, "w", encoding="utf-8") as f:
            json.dump(env_dict, f, indent=2, ensure_ascii=False)

        print(f"Dados de envs salvos com sucesso em: {self.env_path}")

    def save_requests(self, store: Gio.ListStore):

        self._request_group.children = []
        for i in range(store.get_n_items()):
            objeto = store.get_item(i)
            self._request_group.children.append(objeto)

        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(self._request_group.to_dict(), f, indent=2, ensure_ascii=False)

        print(f"Dados salvos com sucesso em: {self.data_path}")

    @staticmethod
    def add_item_to_object(item: list[RequestItem], id: str, new_item: RequestItem):
        if isinstance(item, RequestGroup):
            if item.id == id:
                item.children.append(new_item)
                return True

            for valor in item.children:
                if DataManagement.add_item_to_object(valor, id, new_item):
                    return True

        elif isinstance(item, list):
            for child in item:
                if DataManagement.add_item_to_object(child, id, new_item):
                    return True

        return False

    @staticmethod
    def add_item(item_list: list[RequestItem], id: str, new_item: RequestItem):
        for item in item_list:
            DataManagement.add_item_to_object(item, id, new_item)

    @staticmethod
    def find_item_index(store: Gio.ListStore, id: str):
        for index in range(store.get_n_items()):
            item = store[index]

            if item.id == id:
                finded, position = store.find(item)
                if finded:
                    return finded, position, store
                return False

            item_type = GObject.type_name(item.__gtype__)
            if item_type == "Request":
                continue

            finded = DataManagement.find_item_index(item.children, id)
            if finded:
                return finded
        return False

    @staticmethod
    def remove_by_id(store: Gio.ListStore, id: str):
        finded, position, finded_store = DataManagement.find_item_index(store, id)
        if finded:
            finded_store.remove(position)

    @staticmethod
    def rename_item(store: Gio.ListStore, id: str, new_name: str):
        finded, position, finded_store = DataManagement.find_item_index(store, id)
        if finded:
            finded_store[position].name = new_name
