from fastapi import APIRouter

from controllers.hand_move import hand_move_handler, MouseState
from controllers.types import MouseStateModel


from utils import convert_named_tuple_to_dict

mouse_api = APIRouter(prefix="/mouse")


@mouse_api.get("/state")
async def get_mouse_state():
    return convert_named_tuple_to_dict(hand_move_handler.state)


@mouse_api.put("/state")
async def set_mouse_state(state: MouseStateModel):
    hand_move_handler.state = state.model_dump()
    return convert_named_tuple_to_dict(hand_move_handler.state)
