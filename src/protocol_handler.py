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
class ParseError(Exception):
    """Custom exception for parse errors."""
    pass

@dataclass
class Simplestring:
    data: str

    def __post_init__(self):
        if self.data is None:
            return ""

@dataclass
class Error:
    err_string: str
    err_arr = ["Err", "Errno", "WRONGTYPE", "Error"]
    data = 'Err'

    def __post_init__(self):
        if self.data is None:
            return ""


@dataclass
class Integer:
    data: int

    def __post_init__(self):
        if self.data is None:
            return ""

@dataclass
class Bulkstring:
    data: str

    def __post_init__(self):
        if self.data is None:
            return ""

@dataclass
class Array:
    data: list

    def __post_init__(self):
        if self.data is None:
            return ""

    def __getitem__(self, key):
        return self.data[key]


    def __setitem__(self, key, value):
        self.data[key] = value

    def keys(self):
        return self.data.keys()


class Parser:
    def __init__(self, buffer):
        self.buffer = buffer

    def parse_frame(self, buffer):
        """
        Parses a RESP buffer.
        Args: buffer (bytes): The buffer containing the frame data.
        Returns: tuple: (frame, size)
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
                return Simplestring(value), sep + 2

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
                if len(buffer) < end + 2 or buffer[end:end + 2] != b'\r\n':
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
                total_size = pos  # Start from just after header

                for _ in range(count):
                    if pos >= len(buffer):
                        return None, 0

                    element, size = self.parse_frame(buffer[pos:])
                    if size == 0:
                        return None, 0
                    elements.append(element)
                    pos += size
                    total_size += size

                return elements, total_size

            case _:
                # Unknown frame type
                return None, 0
