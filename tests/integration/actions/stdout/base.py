""" base class for stdout interactive tests
"""
import difflib
import json
import os

import pytest

from ..._common import fixture_path_from_request
from ..._common import update_fixtures
from ..._common import TmuxSession
from ....defaults import FIXTURES_DIR

TEST_FIXTURE_DIR = os.path.join(FIXTURES_DIR, "integration/actions/stdout")
ANSIBLE_PLAYBOOK = os.path.join(TEST_FIXTURE_DIR, "site.yml")
TEST_CONFIG_FILE = os.path.join(TEST_FIXTURE_DIR, "ansible-navigator.yml")


class BaseClass:
    """base class for interactive stdout tests"""

    UPDATE_FIXTURES = False

    @staticmethod
    @pytest.fixture(scope="module", name="tmux_session")
    def fixture_tmux_session(request):
        """tmux fixture for this module"""
        params = {
            "window_name": request.node.name,
            "setup_commands": [
                "export ANSIBLE_DEVEL_WARNING=False",
                "export ANSIBLE_DEPRECATION_WARNINGS=False",
                "export ANSIBLE_NAVIGATOR_PLAYBOOK_ARTIFACT_ENABLE=False",
            ],
            "config_path": TEST_CONFIG_FILE,
            "pane_height": "100",
        }
        with TmuxSession(**params) as tmux_session:
            yield tmux_session

    def test(self, request, tmux_session, index, user_input, comment, playbook_status):
        # pylint:disable=unused-argument
        # pylint: disable=too-few-public-methods
        # pylint: disable=too-many-arguments

        """test"""
        assert os.path.exists(ANSIBLE_PLAYBOOK)
        assert os.path.exists(TEST_CONFIG_FILE)

        received_output = tmux_session.interaction(
            user_input, wait_on_playbook_status=playbook_status
        )
        if self.UPDATE_FIXTURES:
            update_fixtures(request, index, received_output, comment)
        dir_path, file_name = fixture_path_from_request(request, index)
        with open(f"{dir_path}/{file_name}") as infile:
            expected_output = json.load(infile)["output"]
        assert expected_output == received_output, "\n" + "\n".join(
            difflib.unified_diff(expected_output, received_output, "expected", "received")
        )
