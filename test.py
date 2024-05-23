from typing import NamedTuple


class SizeTuple(NamedTuple):
    width: int
    height: int


class CameraState(NamedTuple):
    is_opened: bool
    size: SizeTuple
    exposure: int


t = CameraState(True, SizeTuple(100, 100), 10)


from utils import convert_named_tuple_to_dict


print(convert_named_tuple_to_dict(t, camelCase=True))
