from unittest import TestCase
from unittest.mock import patch


from controllers.cursor_handle import CursorHandleEnum


class TestCursorHandle(TestCase):

    @patch("controllers.cursor_handle._vscroll")
    @patch("controllers.cursor_handle._mouseDown")
    @patch("controllers.cursor_handle._position")
    @patch("controllers.cursor_handle._moveTo")
    def test_cusor(self):
        pass
