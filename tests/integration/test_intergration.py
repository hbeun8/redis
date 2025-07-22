import pytest

from command_handler import handle_command

import subprocess

from pygments.lexers import data

'''
we need tests for echo, exist, del, incr, decr, list commands, persistance, ping, set and get
'''

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
    yield {"PING": "*1\r\n$4\r\nPING\r\n"}

def test_execute_pong(execute_ping):
    assert execute_ping == "*1\r\n$4\r\nPING\r\n"

@pytest.fixture
def execute_echo(data):
    yield {"ECHO": f"*2\r\n$4\r\nECHO\r\n${len(data)}\r\n{data}\r\n"}

def test_execute_echo(execute_echo):
    assert execute_echo == f"*2\r\n$4\r\nECHO\r\n${len(data)}\r\n{data}\r\n"


def test_echo_integration(server):
    res = subprocess.run(["redis-cli", "ECHO", "HELLO"], stdout=subprocess.PIPE)
    assert res.returncode == 0
    assert res.stdout.decode("utf-8").strip() == "HELLO"

'''**********Edge-Cases**********'''

def test_empty_message():
    return ""

def test_connection_drop_midstream():
    return ""

def test_abrupt_client_shutdown():
    return ""

'''**********Stress Tests**********'''

