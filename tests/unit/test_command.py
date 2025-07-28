import pytest
from time import sleep, time_ns
from protocol_handler import Bulkstring, Array, Error, Integer, Simplestring
from command_handler import handle_command
from connection_handler import ConnectionHandler as c
from datastore import Datastore
import datetime

@pytest.fixture
def set_key_value():
    datastore_1 = {"key1": "value", "Expiry": "July 23, 2026, 2:30 PM"}
    command = "SET"
    result = handle_command(command, datastore_1)
    return result

def test_set_key_value(set_key_value):
    result = set_key_value
    assert result == "OK"

@pytest.fixture
def get_key_value():
    datastore_2 = {"key1": "none", "Expiry": "July 25, 2026, 2:30 PM", "type": "value"}
    command = "GET"
    result = handle_command(command, datastore_2)
    return result

def test_get_key_value(get_key_value):
    result = get_key_value
    assert result == 'value'


@pytest.fixture
def get_key_value_expired():
    datastore_3 = {"key3": "value", "Expiry": "July 23, 2025, 2:30 PM", "type": "value"}
    command = "GET"
    result = handle_command(command, datastore_3)
    return result

# This is because we dont have any data at the moment.
def test_get_key_value_expired(get_key_value_expired):
    result = get_key_value_expired
    assert result == '(nil)'


@pytest.fixture
def execute_ping():
    datastore_4 = {"PING" : "NONE"}
    command = "PING"
    result = handle_command(command, datastore_4)
    return result

def test_execute_ping(execute_ping):
    result = execute_ping
    assert result ==  "PONG"


@pytest.mark.parametrize(
    "command_and_datastore,expected",
    [
        # Exists
        (Array([Bulkstring("exists")]), Error("Err wrong number of arguments for 'exists' command")),
        (Array([Bulkstring("exists"), Bulkstring("invalid key")]), Integer(0)),
        (Array([Bulkstring("exists"), Bulkstring("key")]), Integer(1)),
        (Array([Bulkstring("exists"), Bulkstring("invalid key"), Bulkstring("key")]), Integer(1)),

        # Set
        (Array([Bulkstring("set")]), Error("ERR wrong number of arguments for 'set' command")),
        (Array([Bulkstring("set"), Bulkstring("key")]), Error("ERR wrong number of arguments for 'set' command")),
        (Array([Bulkstring("set"), Bulkstring("key"), Bulkstring("value")]), Simplestring("OK")),

        # Set with expire errors
        (Array([Bulkstring("set"), Bulkstring("key"), Bulkstring("value"), Bulkstring("ex")]),
         Error("ERR syntax error")),
        (Array([Bulkstring("set"), Bulkstring("key"), Bulkstring("value"), Bulkstring("px")]),
         Error("ERR syntax error")),
        (Array([Bulkstring("set"), Bulkstring("key"), Bulkstring("value"), Bulkstring("foo")]),
         Error("ERR syntax error")),

        # Get
        (Array([Bulkstring("get")]), Error("ERR wrong number of arguments for 'get' command")),
        (Array([Bulkstring("get"), Bulkstring("key")]), Bulkstring("value")),
        (Array([Bulkstring("get"), Bulkstring("invalid key")]), Bulkstring(None)),

        # Unknown
        (Array([Bulkstring("foo")]), Error("ERR unknown command 'foo', with args beginning with: ")),
        (Array([Bulkstring("foo"), Bulkstring("key")]), Error("ERR unknown command 'foo', with args beginning with: 'key'")),
        (Array([Bulkstring("foo"), Bulkstring("key bar")]), Error("ERR unknown command 'foo', with args beginning with: 'key bar'")),

        # Del
        (Array([Bulkstring("del")]), Error("ERR wrong number of arguments for 'del' command")),
        (Array([Bulkstring("del"), Bulkstring("del key")]), Integer(1)),
        (Array([Bulkstring("del"), Bulkstring("invalid key")]), Integer(0)),
        (Array([Bulkstring("del"), Bulkstring("del key2"), Bulkstring("invalid key")]), Integer(1)),

        # Incr
        (Array([Bulkstring("incr")]), Error("ERR wrong number of arguments for 'incr' command")),
        (Array([Bulkstring("incr"), Bulkstring("key")]), Error("ERR value is not an integer or out of range")),

        # Decr
        (Array([Bulkstring("decr")]), Error("ERR wrong number of arguments for 'decr' command")),

        # Lpush
        (Array([Bulkstring("lpush")]), Error("ERR wrong number of arguments for 'lpush' command")),

        # Rpush
        (Array([Bulkstring("rpush")]), Error("ERR wrong number of arguments for 'rpush' command")),
    ],
)

def test_handle_command(command_and_datastore, expected):
    command = command_and_datastore[0]
    #command = command.data
    datastore = {}
    try:
        datastore = command_and_datastore[1]
        try:
            command = command.data.data
        except AttributeError:
            command = command.data
        datastore = {f"item_{i}": item.data for i, item in enumerate(datastore)}
    except IndexError:
        pass
    expected = expected
    result = handle_command(command, datastore)
    assert result == expected


def test_handle_incr_command_valid_key():
    datastore = Datastore({"ki": 0, "Expiry": "None"})
    result = handle_command("INCR", datastore)
    assert result == Integer(1)
    result = handle_command("INCR", datastore)
    assert result == Integer(2)


def test_handle_decr():
    datastore = Datastore({"kd": 0, "Expiry": "None"})
    result = handle_command("incr", datastore)
    assert result == "(integer) 1"
    result = handle_command("incr", datastore)
    assert result == Integer(2)
    result = handle_command("decr", datastore)
    assert result == Integer(1)
    result = handle_command("decr", datastore)
    assert result == Integer(0)


def test_handle_decr_invalid_key():
    datastore = Datastore({"missing"})
    result = handle_command(Array([Bulkstring("decr"), Bulkstring("missing")]), datastore)
    assert result == Error("ERR value is not an integer or out of range")


def test_handle_lpush_lrange():
    datastore = Datastore({"klp"})
    result = handle_command(Array([Bulkstring("lpush"), Bulkstring("klp"), Bulkstring("second")]), datastore)
    assert result == Integer(1)
    datastore = Datastore({"klp"})
    result = handle_command(Array([Bulkstring("lpush"), Bulkstring("klp"), Bulkstring("first")]), datastore)
    assert result == Integer(2)
    datastore = Datastore({"klp"})
    result = handle_command(Array([Bulkstring("lrange"), Bulkstring("klp"), Bulkstring("0"), Bulkstring("2")]), datastore)
    datastore = Datastore({"klp"})
    assert result == Array([Bulkstring("first"), Bulkstring("second")])


def test_set_with_expiry():
    key = "key"
    value = "value"
    ex = 1  # seconds
    command = [
        Bulkstring("set"), Bulkstring(key), Bulkstring(value),
        Bulkstring("ex"), Bulkstring(str(ex).encode())
    ]
    expected_expiry = time_ns() + ex * 10**9
    result = handle_command(command, datastore)
    assert result == Simplestring("OK")
    stored = datastore._data[key]
    assert stored.value == value
    assert abs(expected_expiry - stored.expiry) < 10**7

    # milliseconds
    px = 100
    command = [
        Bulkstring("set"), Bulkstring(key), Bulkstring(value),
        Bulkstring("px"), Bulkstring(str(px).encode())
    ]
    expected_expiry = time_ns() + px * 10**6
    result = handle_command(command, datastore)
    assert result == Simplestring("OK")
    stored = datastore._data[key]
    assert stored.value == value
    assert abs(expected_expiry - stored.expiry) < 10**7


def test_get_with_expiry():
    px = 100
    command = [
        Bulkstring("set"), Bulkstring("key"), Bulkstring("value"),
        Bulkstring("px"), Bulkstring(str(px).encode())
    ]
    result = handle_command(command, datastore)
    assert result == Simplestring("OK")
    sleep((px + 100) / 1000)
    result = handle_command([Bulkstring("get"), Bulkstring("key")], datastore)
    assert result == Bulkstring(None)
