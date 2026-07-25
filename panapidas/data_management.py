import sys
import os
import json

import gi
from gi.repository import GLib

from panapidas.model.requests import RequestGroup

APPLICATION_NAME = "panapidas"
APPLICATION_DATA_FILENAME = "requests.json"

class DataManagement():

    def __init__(self):
        self.data_dir = GLib.get_user_data_dir()
        self.app_dir = os.path.join(self.data_dir, APPLICATION_NAME)
        self.data_path = os.path.join(self.app_dir, APPLICATION_DATA_FILENAME)

    def load(self) -> RequestGroup:
        if not os.path.exists(self.data_path):
            print("Arquivo não encontrado. Retornando lista vazia.")
            return []

        with open(self.data_path, "r", encoding="utf-8") as f:
            requests_dict = json.load(f)

        return RequestGroup(requests_dict["id"], requests_dict["name"], requests_dict["children"])

    def save(self, requestGroup: RequestGroup):
        os.makedirs(self.app_dir, exist_ok=True)

        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(requestGroup.to_dict(), f, indent=2, ensure_ascii=False)

        print(f"Dados salvos com sucesso em: {self.data_path}")

    @staticmethod
    def add_item(item, id: str, new_item):
        if isinstance(item, RequestGroup):
            if item.id == id:
                item.children.append(new_item)
                return True

            for valor in item.children:
                if DataManagement.add_item(valor, id, new_item):
                    return True

        elif isinstance(item, list):
            for child in item:
                if DataManagement.add_item(child, id, new_item):
                    return True

        return False

