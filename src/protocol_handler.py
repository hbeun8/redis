"""
Redis Protocol Parser

This module implements the Redis Serialization Protocol (RESP) parser.
It handles parsing of the following data types:
- Simple strings (prefixed with +)
- Errors (prefixed with -)
- Integers (prefixed with :)
- Bulk strings (prefixed with $)
- Arrays (prefixed with *)
"""

from dataclasses import dataclass

@dataclass
class SimpleString:
    data: str

def Error(data: str):
    err_arr = ["Err", "Errno", "WRONGTYPE", "Error"]
    for err in err_arr:
        foundErr = data.find(err)
        if foundErr == -1:
            return None
        return err

@dataclass
class Integer:
    data: int

@dataclass
class Bulkstring:
    data: str

@dataclass
class Array:
    data: list

def parse_frame(buffer):
    """
    @Purpose: Parses a Redis protocol frame from the buffer.
    @Args: buffer (bytes): The buffer containing the frame data
    @Returns: tuple: (frame, size)
    """
    if not buffer or len(buffer) < 3:
        return None, 0

    frame_type = buffer[0:1]
    sep = buffer.find(b'\r\n')
    match frame_type:
        case b'+':
            # Simple String
            if sep == -1:
                return None, 0
            value = buffer[1:sep].decode()
            return SimpleString(value), sep + 2

        case b'-':
            # Error
            if sep == -1:
                return None, 0
            message = buffer[1:sep].decode()
            return Error(message), sep + 2

        case b':':
            # Integer
            if sep == -1:
                return None, 0
            value = int(buffer[1:sep])
            return Integer(value), sep + 2

        case b'$':
            # Bulk String
            if sep == -1:
                return None, 0
            length = int(buffer[1:sep])
            start = sep + 2
            end = start + length
            if len(buffer) < end + 2 or buffer[end:end +2] != b'\r\n':
                return None, 0
            value = buffer[start:end].decode()
            return Bulkstring(value), end + 2

        case b'*':
            # Array
            if sep == -1:
                return None, 0

            count = int(buffer[1:sep])
            pos = sep + 2
            elements = []
            agg_size = 0
            for _ in range(count):
                if pos >= len(buffer):
                   return None, 0
                print("pos", pos)
                print("Bufffer", buffer[pos:])
                element, size = parse_frame(buffer[pos:])
                print("element", element)
                print("size", size)
                if element is None:
                    size = 0

                elements.append(element)
                print("elements", elements)
                pos += size
                agg_size += size

            return elements, agg_size

        case _:
            # Unknown frame type
            return None, 0