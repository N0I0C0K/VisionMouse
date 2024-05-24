from enum import Enum


class DictEnum(Enum):
    @classmethod
    def names(cls):
        return cls._member_map_.keys()

    @classmethod
    def values(cls):
        return cls._value2member_map_.keys()

    @classmethod
    def has(cls, key: str) -> bool:
        return key in cls._member_map_
