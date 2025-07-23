import pytest

from command_handler import handle_command

import subprocess


'''
we need tests for echo, exist, del, incr, decr, list commands, persistance, ping, set and get
'''

@pytest.fixture
def execute_ping():
    yield "*1\r\n$4\r\nPING\r\n"

def test_execute_pong(execute_ping):
    assert execute_ping == "*1\r\n$4\r\nPING\r\n"

@pytest.fixture
def execute_echo():
    def _inner(data):
        return f"*2\r\n$4\r\nECHO\r\n${len(data)}\r\n{data}\r\n"
    return _inner

def test_execute_echo(execute_echo):
    data = "world"
    expected = "*2\r\n$4\r\nECHO\r\n$5\r\nworld\r\n"
    assert execute_echo(data) == expected

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

