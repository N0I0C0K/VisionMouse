from unittest import TestCase
from controllers.flow import _jump_false, _jump_true


class TestFlowNode(TestCase):
    def test_jump_func(self):
        data = [True, False, False]

        assert _jump_true(data) == False
        assert _jump_false(data) == True

        data = [False, True, True]

        assert _jump_false(data) == False
        assert _jump_true(data) == True

        data = [True, True, True]

        assert _jump_false(data) == False
        assert _jump_true(data) == False
