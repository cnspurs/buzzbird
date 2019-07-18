import instaloader
import pytest
from core.instagram_v2 import convert_username_to_id


@pytest.mark.parametrize(
    "username, expected",
    [
        ('dele', '183718823'),
    ]
)
def test_convert_instagram_username_to_userid_correctly(username, expected):
    assert convert_username_to_id(username) == expected


@pytest.mark.parametrize(
    "username, expected",
    [
        ('dele213123', ''),
    ]
)
def test_convert_instagram_username_to_userid_incorrectly(username, expected):
    with pytest.raises(instaloader.exceptions.ProfileNotExistsException):
        assert convert_username_to_id(username) == expected
