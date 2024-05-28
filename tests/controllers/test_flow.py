from unittest import TestCase
from unittest.mock import patch, MagicMock
from controllers.flows.flow import _jump_false, _jump_true, flow_manager


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

    @patch("controllers.flow.run_flow")
    async def test_start_flow_async(self, mock_run_flow: MagicMock):
        mock_run_flow.return_value = None

        flow_manager.start(True)

        assert mock_run_flow.assert_called()
        assert flow_manager._running == True

        await flow_manager.stop()

        assert flow_manager._running == False
