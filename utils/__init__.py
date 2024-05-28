import logging
import logging.handlers
import os
import sys

from typing import NamedTuple, Any
from utils.types import Position

logger = logging.getLogger("vision_mouse")
logger.setLevel(logging.INFO)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(
    logging.Formatter("%(name)s %(asctime)s %(module)s: %(message)s")
)
logger.addHandler(stdout_handler)

config = {"is_dev": os.getenv("is_dev", "1") == "1"}


def convert_str_to_camelCase(src: str) -> str:
    sp = src.split("_")
    return sp[0] + "".join(map(lambda x: x.capitalize(), sp[1:]))


def convert_named_tuple_to_dict(
    tar: NamedTuple, *, camelCase: bool = False
) -> dict[str, Any]:
    t_dict = tar._asdict()
    for key, val in t_dict.items():
        if hasattr(val, "_asdict"):
            t_dict[key] = convert_named_tuple_to_dict(val, camelCase=camelCase)
    if camelCase:
        camel_dict = {}
        for key in t_dict:
            camel_dict[convert_str_to_camelCase(key)] = t_dict[key]
        t_dict = camel_dict
    return t_dict


def convert_snake_case_dict_to_camelCase(src: dict[str, Any]) -> dict[str, Any]:
    camel_dict = {}
    for key, val in src.items():
        if isinstance(val, dict):
            camel_dict[convert_str_to_camelCase(key)] = (
                convert_snake_case_dict_to_camelCase(val)
            )
        else:
            camel_dict[convert_str_to_camelCase(key)] = val
    return camel_dict


def distance(pos1: Position, pos2: Position) -> int:
    return (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2
