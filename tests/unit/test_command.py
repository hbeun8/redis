import pytest
from time import sleep, time_ns
from protocol_handler import Bulkstring, Array, Error, Integer, SimpleString
from command_handler import handle_command
from datastore import Datastore  # assuming this exists


@pytest.fixture
def set_key_value():
    datastore = DataStore()
    handle_command(Array([Bulkstring("set"), Bulkstring("key"), Bulkstring("value")]), datastore)
    return datastore


def test_set_key_value(set_key_value):
    assert set_key_value._data["key"].value == "value"


@pytest.fixture
def get_key_value(set_key_value):
    return handle_command(Array([Bulkstring("get"), Bulkstring("key")]), set_key_value)


def test_get_key_value(get_key_value):
    assert get_key_value == Bulkstring("value")


@pytest.fixture
def execute_ping():
    return handle_command(Array([Bulkstring("PING")]), Datastore())


def test_execute_pong(execute_ping):
    assert execute_ping == SimpleString("PONG")


@pytest.mark.parametrize(
    "command,expected",
    [
        # Echo tests
        (Array([Bulkstring("ECHO")]), Error("Err wrong number of arguments for 'echo' command")),
        (Array([Bulkstring("ECHO"), Bulkstring("Hello"), Bulkstring("World")]),
         Error("Err wrong number of arguments for 'echo' command")),

        # Exists
        (Array([Bulkstring("exists")]), Error("Err wrong number of arguments for 'exists' command")),
        (Array([Bulkstring("exists"), Bulkstring("invalid key")]), Integer(0)),
        (Array([Bulkstring("exists"), Bulkstring("key")]), Integer(1)),
        (Array([Bulkstring("exists"), Bulkstring("invalid key"), Bulkstring("key")]), Integer(1)),

        # Ping
        (Array([Bulkstring("PING")]), SimpleString("PONG")),
        (Array([Bulkstring("ping"), Bulkstring("Hello")]), Bulkstring("Hello")),
        (Array([Bulkstring("PING"), Bulkstring("Hello"), Bulkstring("Hello")]),
         Error("Err wrong number of arguments for 'PING' command")),

        # Set
        (Array([Bulkstring("set")]), Error("ERR wrong number of arguments for 'set' command")),
        (Array([Bulkstring("set"), Bulkstring("key")]), Error("ERR wrong number of arguments for 'set' command")),
        (Array([Bulkstring("set"), Bulkstring("key"), Bulkstring("value")]), SimpleString("OK")),

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
    ]
)
def test_handle_command(command, expected):
    datastore = Datastore({"key": "value", "del key": "value", "del key2": "value"})
    result = handle_command(command, datastore)
    assert result == expected


def test_handle_incr_command_valid_key():
    datastore = Datastore()
    result = handle_command(Array([Bulkstring("incr"), Bulkstring("ki")]), datastore)
    assert result == Integer(1)
    result = handle_command(Array([Bulkstring("incr"), Bulkstring("ki")]), datastore)
    assert result == Integer(2)


def test_handle_decr():
    datastore = Datastore()
    result = handle_command(Array([Bulkstring("incr"), Bulkstring("kd")]), datastore)
    assert result == Integer(1)
    result = handle_command(Array([Bulkstring("incr"), Bulkstring("kd")]), datastore)
    assert result == Integer(2)
    result = handle_command(Array([Bulkstring("decr"), Bulkstring("kd")]), datastore)
    assert result == Integer(1)
    result = handle_command(Array([Bulkstring("decr"), Bulkstring("kd")]), datastore)
    assert result == Integer(0)


def test_handle_decr_invalid_key():
    datastore = Datastore()
    result = handle_command(Array([Bulkstring("decr"), Bulkstring("missing")]), datastore)
    assert result == Error("ERR value is not an integer or out of range")


def test_handle_lpush_lrange():
    datastore = Datastore()
    result = handle_command(Array([Bulkstring("lpush"), Bulkstring("klp"), Bulkstring("second")]), datastore)
    assert result == Integer(1)
    result = handle_command(Array([Bulkstring("lpush"), Bulkstring("klp"), Bulkstring("first")]), datastore)
    assert result == Integer(2)
    result = handle_command(Array([Bulkstring("lrange"), Bulkstring("klp"), Bulkstring("0"), Bulkstring("2")]), datastore)
    assert result == Array([Bulkstring("first"), Bulkstring("second")])


def test_set_with_expiry():
    datastore = Datastore()
    key = "key"
    value = "value"
    ex = 1  # seconds
    command = [
        Bulkstring("set"), Bulkstring(key), Bulkstring(value),
        Bulkstring("ex"), Bulkstring(str(ex).encode())
    ]
    expected_expiry = time_ns() + ex * 10**9
    result = handle_command(command, datastore)
    assert result == SimpleString("OK")
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
    assert result == SimpleString("OK")
    stored = datastore._data[key]
    assert stored.value == value
    assert abs(expected_expiry - stored.expiry) < 10**7


def test_get_with_expiry():
    datastore = Datastore()
    px = 100
    command = [
        Bulkstring("set"), Bulkstring("key"), Bulkstring("value"),
        Bulkstring("px"), Bulkstring(str(px).encode())
    ]
    result = handle_command(command, datastore)
    assert result == SimpleString("OK")
    sleep((px + 100) / 1000)
    result = handle_command([Bulkstring("get"), Bulkstring("key")], datastore)
    assert result == Bulkstring(None)
