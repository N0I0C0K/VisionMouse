import logging
import logging.handlers
import os
import sys

from typing import NamedTuple, Any

logger = logging.getLogger("vision_mouse")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


class NamedTupleDictable(NamedTuple):
    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError()


config = {"is_dev": os.getenv("is_dev", "1") == "1"}
