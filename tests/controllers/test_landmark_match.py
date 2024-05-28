from unittest import TestCase

from utils import Position

from controllers.landmark_match import LandMarkMatch
from controllers.hand_info import HandInfo


def gen_test_hand_info() -> HandInfo:
    pos_list: list[Position] = [(0, 0) for _ in range(21)]
    pos_list[9] = (30, 30)
    hand_info = HandInfo(pos_list, (128, 128), 0)
    return hand_info


class TestLandMarkMatch(TestCase):
    def test_index_match(self):
        hand_info = gen_test_hand_info()

        for matcher in LandMarkMatch:
            res = matcher.match(hand_info)

            assert res == True
