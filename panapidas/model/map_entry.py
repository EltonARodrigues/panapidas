from gi.repository import GObject


class MapEntry(GObject.Object):
    __gtype_name__ = "MapEntry"

    def __init__(self, id: int, key: str, value: str):
        super().__init__()

        self._id = id
        self._key = key
        self._value = value

    @GObject.Property(type=int)
    def id(self) -> int:
        return self._id

    @GObject.Property(type=str)
    def key(self) -> str:
        return self._key

    @GObject.Property(type=str)
    def value(self) -> str:
        return self._value

    @key.setter
    def key(self, key: str):
        self._key = key

    @value.setter
    def value(self, value: str):
        self._value = value

    def __repr__(self):
        return f"MapEntry(id={self.id}, key={self.key}, value={self.value})"

    def __str__(self):
        return f"{self._id} -> ({self._key}:{self._value})"

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
        }

