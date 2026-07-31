import sys
import os
import json

from gi.repository import GLib, GObject, Gio

from panapidas.model.requests import RequestGroup, RequestItem, Request

APPLICATION_NAME = "panapidas"
APPLICATION_DATA_FILENAME = "requests.json"


class DataManagement:

    def __init__(self):
        self.data_dir = GLib.get_user_data_dir()
        self.app_dir = os.path.join(self.data_dir, APPLICATION_NAME)
        self.data_path = os.path.join(self.app_dir, APPLICATION_DATA_FILENAME)
        self._request_group = None

    def load(self) -> RequestGroup:
        if not os.path.exists(self.data_path):
            print("Arquivo não encontrado. Retornando lista vazia.")
            return RequestGroup("ROOT", "", [])

        with open(self.data_path, "r", encoding="utf-8") as f:
            requests_dict = json.load(f)

        self._request_group = RequestGroup(
            requests_dict["id"], requests_dict["name"], requests_dict["children"]
        )
        return self._request_group

    def save(self, store: Gio.ListStore):
        os.makedirs(self.app_dir, exist_ok=True)

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
