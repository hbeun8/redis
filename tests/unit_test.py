
# Purpose:
# The aim is to have tests for
# 1. streams of data flowing from redis-cli (assumed we buffer w. RESP serialization)
# 2. streams will be a partial message, a whole message and a whole message followed by 1 or 2

import pytest
from protocol_handler import parse_frame, SimpleString, Error, Integer, Bulkstring  # Adjust imports as needed

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

    #RESP OPRATORS:
    # We want firstly to connect to the server and with the chosen command and ping a message and then close the connection
    #(b"+full\r\n", (Server(args.e).send(b"+full\r\n")).recv(), "full"),  #    # Echo Loop
  #  (SET (b"+HELLO\r\n",b"+VALUE\r\n") , (Server(args.s).send(set(b"+HELLO"\r\n", b"*2\r\n"VALEU"\r\n").recv(), "\n"),  # SET (Key, Value)
  #  (GET (b"+HELLO\r\n", b"+VALUE\r\n"), (Server(args.g).send(set(b"+HELLO"\r\n", b" * 2\r\n"VALEU"\r\n").recv(), "full"),  # GET (Key)

    #Connection Handler
    #We want this to connect to the server using the correct option and perform one of operations and also pipelines.
    # if in the pipeline we want it to go on until there is a keyboard interruption



     ])
def test_parse_frame(buffer, expected):
    frame, size = parse_frame(buffer)
    assert frame == expected[0]
    assert size == expected[1]
