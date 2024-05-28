from controllers.cursor_handle import direction, move, current_position
from controllers.hand_info import HandInfo
from filter import SlidingWindowMeanFilter
from utils.iter import min_item


from math import floor, sqrt


class HandMoveHandler:
    def __init__(self) -> None:
        self.pos_filter: SlidingWindowMeanFilter[int] = SlidingWindowMeanFilter(5)
        self.last_hand = None

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
        scale = speed / 10 * pow(max(speed, 0.0001), 0.1)

        return move(floor(x_dir * scale), floor(y_dir * scale))


hand_move_handler = HandMoveHandler()
