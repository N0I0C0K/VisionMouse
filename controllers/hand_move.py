from math import floor, sqrt
from typing import NamedTuple

from controllers.cursor_handle import move, current_position
from controllers.hand_info import HandInfo
from controllers.types import PositionTuple
from filter import SlidingWindowMeanFilter


class MouseState(NamedTuple):
    base_speed: float
    acceleration: float
    pos: PositionTuple


def direction(t: tuple[float, float]) -> tuple[float, float]:
    x, y = t
    dis = max(sqrt(x * x + y * y), 0.001)
    return x / dis, y / dis


class HandMoveHandler:
    def __init__(self) -> None:
        self.pos_filter: SlidingWindowMeanFilter[int | float] = SlidingWindowMeanFilter(
            5
        )
        self.last_hand = None
        self.base_speed = 0.1
        self.acceleration = 0.1

    def forward(self, hand_info: HandInfo):
        cur_hand = hand_info  # self.get_the_right_hand(hand_info_list)
        last_hand = self.last_hand
        self.last_hand = cur_hand
        if not last_hand:
            return current_position()

        pos_filter = self.pos_filter
        (dx, dy), dt = cur_hand.anchor_diff(last_hand)
        dt = max(dt, 0.01)
        dx, dy = map(int, pos_filter.push((dx, dy)))
        x_dir, y_dir = direction((dx, dy))
        speed = sqrt(dx**2 + dy**2) / max(dt, 0.001)
        scale = speed * self.base_speed * pow(max(speed, 0.0001), self.acceleration)

        return move(floor(x_dir * scale), floor(y_dir * scale))

    @property
    def state(self) -> MouseState:
        cur_pos = current_position()
        return MouseState(self.base_speed, self.acceleration, PositionTuple(*cur_pos))

    @state.setter
    def state(self, val: dict):
        if "baseSpeed" in val and val["baseSpeed"] is not None:
            self.base_speed = float(val["baseSpeed"])
        if "acceleration" in val and val["acceleration"] is not None:
            self.acceleration = float(val["acceleration"])


hand_move_handler = HandMoveHandler()
