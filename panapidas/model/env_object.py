import uuid

from gi.repository import GObject

from panapidas.model.map_entry import MapEntry


class EnvObject(GObject.Object):
    __gtype_name__ = "EnvObject"

    def __init__(self, id=None, name=None, envs_map=[]):
        super().__init__()

        self._id = str(uuid.uuid4()) if id is None else id
        self._name = name
        self.envs = EnvObject.map_builder(envs_map)

    @GObject.Property(type=int)
    def id(self) -> int:
        return self._id

    @GObject.Property(type=str)
    def name(self) -> str:
        return self._name

    @staticmethod
    def map_builder(envs_map):
        return [
            MapEntry(id=env.get("id"), key=env.get("key"), value=env.get("value"))
            for env in envs_map
        ]

    def to_dict(self) -> dict[str, any]:
        return {
            "id": self.id,
            "name": self.name,
            "envs_map": [env_map.to_dict() for env_map in self.envs],
        } 