
import pytest

from protocol_handler import Bulkstring, Array, Error, Integer, Simplestring
from command_handler import handle_command
from connection_handler import ConnectionHandler as c
from datastore import Datastore



@pytest.mark.parametrize(
    "command, datastore, expected",
    [
        # exists
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
    ds = Datastore({"ki": 0, "Expiry": "None"})
    ds.Add("k", 1)
    result = handle_command(command, datastore)
    assert result == expected

'''
Checks
- Null Expiry
- LAdd Expiry
- RAdd Expiry
- RSort
- passive_delete_expiry

WE want to check CAT
length of expiry_table = number of items with expiry
check_if_current_items_are_not_expired
expire and item and it reacts positively to set and get commands
'''

