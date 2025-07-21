import pytest

from command_handler as handle_command
from rich.style import NULL_STYLE


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

def test_empty_message():
    with pytest.raises(ValueError):
        return NULL

def test_connection_drop_midstream():


def test_abrupt_client_shutdown():


'''**********Stress Tests**********'''

def test_send10kmessages():


def test_handle1_10k_connections():
