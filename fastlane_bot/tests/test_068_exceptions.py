# ------------------------------------------------------------
# Auto generated test file `test_068_exceptions.py`
# ------------------------------------------------------------
# source file   = NBTest_068_exceptions.py
# test id       = 068
# test comment  = exceptions
# ------------------------------------------------------------


import pytest

from fastlane_bot.events.exceptions import AsyncUpdateRetryException


@pytest.mark.parametrize(
    "message, id",
    [
        ("Failed to update, retrying...", 'happy-1'),
        ("Update failed at step 3, retrying...", 'happy-2'),
        ("Temporary network issue, attempt retry...", 'happy-3'),
    ],
)
def test_aync_update_retry_exception_with_message(message, id):
    # Act
    exception = AsyncUpdateRetryException(message)

    # Assert
    assert str(exception) == message, f"Test case {id} failed: The exception message does not match the expected message."

@pytest.mark.parametrize(
    "message, id",
    [
        ("", 'edge-1'),
    ],
)
def test_aync_update_retry_exception_with_empty_message(message, id):
    # Act
    exception = AsyncUpdateRetryException(message)

    # Assert
    assert str(exception) == message, f"Test case {id} failed: The exception message should be empty."

@pytest.mark.parametrize(
    "message, id",
    [
        ('happy-1', 'happy-1'),
        (None, 'happy-2'),
        ('3', 'happy-3'),
    ],
)
def test_aync_update_retry_exception_raises(message, id):
    # Act & Assert
    with pytest.raises(AsyncUpdateRetryException, match=message):
        raise AsyncUpdateRetryException(message)