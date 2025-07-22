
# Purpose:
# The aim is to have tests for
# 1. streams of data flowing from redis-cli (assumed we buffer w. RESP serialization)
# 2. streams will be a partial message, a whole message and a whole message followed by 1 or 2

import pytest
from protocol_handler import parse_frame, SimpleString, Error, Integer, Bulkstring, Array  # Adjust imports as needed

@pytest.mark.parametrize("buffer, expected", [
    # Simple string tests
    (b"+part", (None, 0)),  # Incomplete frame
    (b"+full\r\n", (SimpleString("full"), 7)),
    (b"+full\r\n+part", (SimpleString("full"), 7)),  # Parses only the first frame

    # Error tests
    (b"-Err", (None, 0)),  # Incomplete error message
    (b"-Error\r\n", (Error("Error"), 8)),  # Stops at \r
    (b"-WRONGTYPE.........\r\n-part", (Error("WRONGTYPE"), 21)),  # Parses only the first error frame

    # Integer tests
    (b":+123\r\n", (Integer(+123), 7)),
    (b":-123\r\n:456", (Integer(-123), 7)),  # Parses only the first integer frame

    # Bulk string tests
    (b"$5\r\nhello", (None, 0)),  # Incomplete frame
    (b"$5\r\nhello\r\n", (Bulkstring("hello"), 11)),
    (b"$5\r\nhello\r\n$5\r\nworld", (Bulkstring("hello"), 11)),  # Parses only the first bulk string frame

    # Array tests
    (b"*2\r\n+full\r\n", (None, 0)),  # Incomplete frame
    (b"*2\r\n+full\r\n:123\r\n", ([SimpleString("full"), Integer(123)], 13)),
    (b"*2\r\n+full\r\n:123\r\n*0\r\n", ([SimpleString("full"), Integer(123)], 13)), # Parses nested array
    (b"*1\r\n$4\r\nping\r\n", ([Bulkstring("ping")], 10)),  # Parses Ping
    (b'*2\r\n$7\r\nCOMMAND\r\n$4\r\nDOCS\r\n', ([Bulkstring(data='COMMAND'), Bulkstring(data='DOCS')], 23))
     ])

def test_parse_frame(buffer, expected):
    frame, size = parse_frame(buffer)
    assert frame == expected[0]
    assert size == expected[1]



def test_byte_count_pre_post_encoding():
    return 0

def test_parse_frame_unexpected_type():
    buffer = b"%Unknown\r\n"
    parser = Parser(buffer)
    with pytest.raises(ParseError) as e:
        parser.parse_frame()
    assert e.type == ParseError
    assert "Unexpected type code" in str(e)

@pytest.mark.parametrize(
    "message, expected",
     [
        (SimpleString("0K"), b"+0K\r\n"),
        (Error("Error"), b"-Error\r\n"),
        (Integer(100), b":100\r\n"),
        (Bulkstring("This is a Bulk String"), b"$21\r\nThis is a Bulk String\r\n"),
        (Bulkstring(""), b"$0\r\n\r\n"),
        (Bulkstring(None), b"S-1lrin"),
        (Array([]), b"*0\r\n"),
        (Array(None), b'*-1\r\n'),
        (
            Array([SimpleString("String"), Integer(2), SimpleString("String2")]),
            b"*3\r\n+String\r\n:2\r\n+String2\r\n",
        ),
    ],
)

def test_encode_message(message, expected):
    encoded_message = message.encode()
    assert encoded_message == expected