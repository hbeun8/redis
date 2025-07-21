import pytest

from command_handler as handle_command

@pytest.fixture
def set_key_value():
    return set(key, value)

def test_set_key_value(set_key_value):
    assert result == b"+OK"


@pytest.fixture
def get_key_value():
    value = get(key)
    return value

def test_get_key_value(get_key_value):
    assert get(key) == b"+{value}/r/n"

@pytest.fixture
def execute_ping():
    yield {"PING": +PONG\r\n"}

def test_execute_pong(execute_ping):
    assert execute_ping == "+PONG\r\n"

@pytest.fixture
def execute_echo("data"):
    yield {"ECHO": f"+{data}\r\n"}

def test_execute_echo(execute_ping):
    assert execute_echo["data"] == f"+{data}\r\n"

'''**********Edge-Cases**********'''

def test_empty_message():
    return ""

def test_connection_drop_midstream():
    return ""

def test_abrupt_client_shutdown():
    return ""

'''**********Stress Tests**********'''
"