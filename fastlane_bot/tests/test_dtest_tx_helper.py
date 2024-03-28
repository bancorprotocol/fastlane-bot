import json

import pytest
from unittest.mock import patch, MagicMock

from fastlane_bot.tests.deterministic.dtest_tx_helper import TestTxHelper


@pytest.fixture
def mock_logger():
    return MagicMock()


def test_find_most_recent_log_folder(mocker):
    mocker.patch('glob.glob', return_value=['./logs/folder1', './logs/folder2'])
    mocker.patch('os.path.isdir', side_effect=lambda x: True)
    mocker.patch('os.path.getmtime', side_effect=lambda x: {'./logs/folder1': 1, './logs/folder2': 2}[x])

    assert TestTxHelper.find_most_recent_log_folder() == './logs/folder2'


def test_wait_for_file_exists_before_timeout(mocker, mock_logger):
    mocker.patch('os.path.exists', return_value=True)
    assert TestTxHelper.wait_for_file("dummy_path", mock_logger) is True
    mock_logger.debug.assert_called_with("File found.")


def test_wait_for_file_timeout(mocker, mock_logger):
    mocker.patch('os.path.exists', return_value=False)
    mocker.patch('time.time', side_effect=[0, 0, 121])  # Simulating timeout
    assert TestTxHelper.wait_for_file("dummy_path", mock_logger, timeout=120) is False
    mock_logger.debug.assert_called_with("Timeout waiting for file.")

def test_load_json_data(tmpdir):
    # Create a temporary JSON file
    file = tmpdir.join("test.json")
    data = {"key": "value"}
    file.write(json.dumps(data))

    # Test loading the JSON data
    loaded_data = TestTxHelper.load_json_data(str(file))
    assert loaded_data == data
