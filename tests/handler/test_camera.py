from unittest import TestCase
from unittest.mock import patch, MagicMock

from .test_base import test_client
from controllers.camera import FrameTuple

from tests.test_helper import get_mock_frame


class TestCamera(TestCase):
    @patch("routes.camera.read_real_time_camera")
    async def test_websocket_real_time_camera(
        self, mock_read_real_time_camera: MagicMock
    ):
        mock_read_real_time_camera.return_value = [
            FrameTuple(get_mock_frame(), 200, 300)
        ]
        with test_client.websocket_connect("/camera/test") as ws:

            data = ws.receive_bytes()

            assert len(data) != 0
