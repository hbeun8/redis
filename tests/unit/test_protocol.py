
# Purpose:
# The aim is to have tests for
# 1. streams of data flowing from redis-cli (assumed we buffer w. RESP serialization)
# 2. streams will be a partial message, a whole message and a whole message followed by 1 or 2

import pytest
from protocol_handler import Parser, ParseError, Simplestring, Error, Integer, Bulkstring, Array  # Adjust imports as needed
from command_handler import resp_encoder_get

@pytest.mark.parametrize("buffer, expected", [
    # Simple string tests
    (b"+part", (None, 0)),  # Incomplete frame
    (b"+full\r\n", (Simplestring("full"), 7)),
    (b"+full\r\n+part", (Simplestring("full"), 7)),  # Parses only the first frame

    # Error tests
    (b"-Err", (None, 0)),  # Incomplete error message
    (b"-Error\r\n", (Error("Error"), 8)),  # Stops at \r

    # Integer tests
    (b":+123\r\n", (Integer(+123), 7)),
    (b":-123\r\n:456", (Integer(-123), 7)),  # Parses only the first integer frame

    # Bulk string tests
    (b"$5\r\nhello", (None, 0)),  # Incomplete frame
    (b"$5\r\nhello\r\n", (Bulkstring("hello"), 11)),
    (b"$5\r\nhello\r\n$5\r\nworld", (Bulkstring("hello"), 11)),  # Parses only the first bulk string frame

    # Array tests
    (b"*2\r\n+full\r\n", (None, 0)),  # Incomplete frame
    (b"*2\r\n+full\r\n:123\r\n", ([Simplestring("full"), Integer(123)], 17)),
    (b"*2\r\n+full\r\n:123\r\n*0\r\n", ([Simplestring("full"), Integer(123)], 17)), # Parses nested array
    (b"*1\r\n$4\r\nping\r\n", ([Bulkstring("ping")], 14)),  # Parses Ping
    (b'*2\r\n$7\r\nCOMMAND\r\n$4\r\nDOCS\r\n', ([Bulkstring(data='COMMAND'), Bulkstring(data='DOCS')], 27))
     ])

def test_parse_frame(buffer, expected):
    parser = Parser(buffer)
    frame, size = parser.parse_frame(buffer)
    assert frame == expected[0]
    assert size == expected[1]

def test_parse_frame_unexpected_type():
    buffer = b"%Unknown\r\n"
    parser = Parser(buffer)
    with pytest.raises(ParseError) as e:
        parser.parse_frame(buffer)
    assert e.type == ParseError
    assert "Unexpected type code" in str(e)

# We are parsing most items as an array, and it seems to be working fine. In some cases as Bulkstring also.
#We are processing as if it is an array
@pytest.mark.parametrize(
    "message, expected",
     [
        ("0K", b'*1\r\n$3\r\n0 K\r\n'),
        ("Error", b'*1\r\n$9\r\nE r r o r\r\n'),
        ("This is a Bulk String", b'*1\r\n$41\r\nT h i s   i s   a   B u l k   S t r i n g\r\n'),
        ("", b""),
        (None, b""),
        ([], b""),
        ([None], b'*-1\r\n'),
        (
            ["String2"],
            b"*1\r\n$7\r\nString2\r\n",
        ),
    ],
)

def test_encode_message(message, expected):

    encoded_message = resp_encoder_get(message).encode()
    assert encoded_message == expected
