import pytest

from command_handler as handle_command

@pytest.fixture
def set_key_value():
    set(key, value)

def test_set_key_value(set_key_value):
    result = set_key_value("hello", "redis")
    assert result == b"+OK"


@pytest.fixture
def get_key_value():
    def set(key: str, value: str):
        return b"+OK"
'''**********Edge-Cases**********'''

def