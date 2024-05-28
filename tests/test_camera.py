import unittest
from unittest.mock import patch, MagicMock

from controllers.camera import read_real_time_camera, camera

from tests.test_helper import *


class TestCamera(unittest.TestCase):
    @patch("controllers.camera.camera.cap")
    def test_get_real_camera(self, mock_app: MagicMock):
        mock_app.isOpened.return_value = True
        test_frame = get_mock_frame()
        mock_app.read.return_value = (True, test_frame)
        mock_app.set.return_value = None
        mock_app.get.return_value = 0
        mock_app.open.return_value = None
        camera.open()
        gen = read_real_time_camera()

        assert camera.cap is not None
        for it in gen:
            assert it.width == 200
            assert it.height == 300
            assert it.frame is not None
            break
