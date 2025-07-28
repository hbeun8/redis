import pytest
from time import sleep, time_ns
from protocol_handler import Bulkstring, Array, Error, Integer, Simplestring
from command_handler import handle_command
from connection_handler import ConnectionHandler as c
from datastore import Datastore
import datetime

from typing_extensions import dataclass_transform


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
    "command, datastore,expected",
    [
        # Exists
        ("exists",[""],  "Err wrong number of arguments for 'exists' command"),
        ("exists", ["invalid key", "None"], "(integer) 0"),
        ("exists", ["key", "None"], "(integer) 1"),
        #multiple keys not catered for:
        #(Array([Bulkstring("exists"), Bulkstring("invalid key"), Bulkstring("key")]), Integer(1)),

        # Set
        ("set", [""] , "-ERR wrong number of arguments for 'set' command"),
        ("set", ["key"], "-ERR wrong number of arguments for 'set' command"),
        ("set",["key", "value"], "+OK"),

        # Set with expire errors
        ("set", ["key", "value", "ex"], "-ERR syntax error"),
        ("set",["key", "value","px"], "-ERR syntax error"),
        ("set", ["key", "value","foo"], "-ERR syntax error"),

        # Get
        ("get", [], "-ERR wrong number of arguments for 'get' command"),
        ("get", ["key"], "value"),
        ("get", ["invalid key"], "(nil)"),

        # Unknown
        ("foo", [], "-ERR unknown command 'foo', with args beginning with: "),
        ("foo",["key"], "-ERR unknown command 'foo', with args beginning with: 'key'"),
        ("foo", ["key", "bar"], "-ERR unknown command 'foo', with args beginning with: 'key bar'"),

        # Del
        ("del", [], "-ERR wrong number of arguments for 'del' command"),
        ("del", ["del", "key"], "(integer) 1"),
        ("del", ["invalid key"], "(integer) 0"),
        # we are not catering for multiple keys to delete
        #("del", ["del" "key2" , "invalid key"], "(integer) 0"),

        # Incr
        ("incr", [], "-ERR wrong number of arguments for 'incr' command"),
        ("incr", ["key"], "-ERR value is not an integer or out of range"),

        # Decr
        ("decr", [], "-ERR wrong number of arguments for 'decr' command"),

        # Lpush
        ("lpush", [],"-ERR wrong number of arguments for 'lpush' command"),

        # Rpush
        ("rpush", [], "-ERR wrong number of arguments for 'rpush' command"),
    ],
)

def test_handle_command(command, datastore, expected):
    ds = Datastore({"ki": 0, "Expiry": "None"}) # initialise the instance
    ds.Add(build(datastore))
    result = handle_command(command, build(datastore))
    assert result == expected


def test_handle_incr_command_valid_key():
    datastore = Datastore({"ki": 0, "Expiry": "None"})
    result = handle_command("INCR", datastore)
    assert result == "(integer) 1"
    result = handle_command("INCR", datastore)
    assert result == "(integer) 2"


def test_handle_decr():
    frames = ["kd", 0, "Expiry", "None"]
    datastore= Datastore(build(frames))
    result = handle_command("incr", datastore)
    assert result == "(integer) 1"
    result = handle_command("incr", datastore)
    assert result ==  "(integer) 2"
    result = handle_command("decr", datastore)
    assert result ==  "(integer) 1"
    result = handle_command("decr", datastore)
    assert result ==  "(integer) 0"


def test_handle_decr_invalid_key():
    frames = ["missing"]
    datastore = Datastore(build(frames))
    result = handle_command("decr", datastore)
    assert result == "-ERR value is not an integer or out of range"


def test_handle_lpush_lrange():
    datastore = Datastore(build(["klp", "second"]))
    result = handle_command("lpush", datastore)
    assert result == "(integer) 1"
    datastore = Datastore(build(["klp", "first"]))
    result = handle_command("lpush", datastore)
    assert result == "(integer) 1"
    datastore = Datastore(build(["klp", "0", "2"]))
    result = handle_command("lrange", datastore)
    datastore = Datastore(build(["klp", "first", "second"]))
    assert result == Array("lrange", datastore)

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


def build(frames):

    def isvalid(data: list, index: int, safe: str):
        try:
            return data[index]
        except Exception:
            return safe

    kwarg_key = isvalid(frames, 0, "None"),
    kwarg_value = isvalid(frames, 1, "None"),
    kwarg_ex_px = isvalid(frames, 2, "Expiry"),
    kwarg_ex_px_value = isvalid(frames, 3, "None"),
    return {kwarg_key[0]: kwarg_value[0], kwarg_ex_px[0]: kwarg_ex_px_value[0]}