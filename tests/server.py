
# Purpose:
# The aim is to have tests for
# 1. tcp/udp options
# 2. sockets objects
# 3. listening
# c4. streams will be a partial message, a whole message and a whole message followed by 1 or 2

import pytest
from protocol_handler import parse_frame, SimpleString, Error, Integer, Bulkstring  # Adjust imports as needed

@pytest.mark.parametrize("buffer, expected", [
    # Server
    ("tcp", (something)),  # Socket object creation (AF_INET, SOCK_STREAM)
    ("udp", (something)),  #
    ("invalid ipaddress", (something)) # invalid IP address

    # Standalong
    ("Echo-SA", (something)),  # Message sent is same as message recieved
    ("Ping-SA", (something)),  # Pong Message is recieved by the client

     ])
def test_server(buffer, expected):
    frame, size = parse_frame(buffer)
    assert frame == expected[0]
    assert size == expected[1]
