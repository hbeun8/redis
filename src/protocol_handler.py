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
    message: str = "Unexpected parse error"

    def __str__(self):
        return self.message


@dataclass
class Simplestring:
    data: str

    def __post_init__(self):
        if self.data is None:
            raise ValueError(None, 0)

    def result(self):
        value = self.data
        return value

@dataclass
class Error:
    data: str

    def __post_init__(self):
        if self.data is None:
            raise ValueError(None, 0)

    def result(self):
        value = self.data
        return value

@dataclass
class Integer:
    data: str

    def __post_init__(self):
        if self.data is None:
            raise ValueError(None, 0)

    def result(self):
        value = self.data
        return value

@dataclass
class Bulkstring:
    data: str

    def __post_init__(self):
        if self.data is None:
            raise ValueError(None, 0)

    def result(self):
        value = self.data
        return value

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
        Args: buffer (bytes): The buffer contains the frame data.
        Returns: tuple: (frame, size)
        """
        if not buffer or len(buffer) < 3:
            return None, 0

        buffer = buffer
        frame_type = buffer[0:1]
        match frame_type:
            case b'+':
                # Simple String
                sep = buffer.find(b'\r\n')
                '''Validation Block'''
                if buffer is None:
                    return None, 0
                if sep == -1:
                    return None, 0
                '''Validation Block'''
                message = buffer[1:sep].decode()
                try:
                    return Simplestring(message), sep + 2
                except ValueError as e:
                    return e
            case b'-':
                # Errors
                sep = buffer.find(b'\r\n')
                '''Validation Block'''
                if buffer is None:
                    return None, 0
                if sep == -1:
                    return None, 0
                '''Validation Block'''
                message = buffer[1:sep].decode()
                try:
                    return Error(message), sep + 2
                except ValueError as e:
                    return e
            case b':':
                # Integer
                sep = buffer.find(b'\r\n')
                '''Validation Block'''
                if buffer is None:
                    return None, 0
                if sep == -1:
                    return None, 0
                '''Validation Block'''
                message = buffer[1:sep].decode()
                try:
                    return Integer(message), sep + 2
                except ValueError as e:
                    return e
            case b'$':
                # Bulk String
                sep = buffer.find(b'\r\n')
                length = int(buffer[1:sep])
                start = sep + 2
                end = start + length
                '''Validation Block'''
                if buffer is None:
                    return None, 0
                if sep == -1:
                    return None, 0
                if len(buffer) < end + 2 or buffer[end:end + 2] != b'\r\n':
                    return None, 0
                '''Validation Block'''
                message = buffer[start:end].decode()
                try:
                    return Bulkstring(message), end + 2
                except ValueError as e:
                    return e
            case b'*':
                # Arrays
                sep = buffer.find(b'\r\n')
                count = int(buffer[1:sep])
                pos = sep + 2
                elements = []
                total_size = pos  # Start from just after header
                '''Validation Block'''
                if buffer is None:
                    return None, 0
                if sep == -1:
                    return None, 0

                '''Validation Block'''
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
                raise ParseError("Unexpected type code")
