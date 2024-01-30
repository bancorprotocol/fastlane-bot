import pytest

from fastlane_bot.events.exceptions import AyncUpdateRetryException


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
    exception = AyncUpdateRetryException(message)

    # Assert
    assert str(exception) == message, f"Test case {id} failed: The exception message does not match the expected message."

# Edge case test with empty string as message
@pytest.mark.parametrize(
    "message, id",
    [
        ("", 'edge-1'),
    ],
)
def test_aync_update_retry_exception_with_empty_message(message, id):
    # Act
    exception = AyncUpdateRetryException(message)

    # Assert
    assert str(exception) == message, f"Test case {id} failed: The exception message should be empty."

# Happy path case test which raises exceptions (should raise AyncUpdateRetryException)
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
    with pytest.raises(AyncUpdateRetryException, match=message):
        raise AyncUpdateRetryException(message)
