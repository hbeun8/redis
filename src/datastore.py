
'''
Datastore 
'''
from threading import Lock

class Datastore:
    def __init__(self):
        self._data = {}
        self._lock = Lock()

    def Get(self, key):
        # Lock not required in read-only mode.
        return self._data.get(key)

    def Add(self, key: str, value: str, expiry:int, type: int ):
        with self._lock:
            if key in self._data:
                print(f"Key {key} already exists")
                return 1  # Don't overwrite
            self._data[key] = value
            return 0

    def __str__(self):
        return f"Datastore({self._data})"

import struct

expiry_ms = 1724189999000  # epoch in ms
packed_expiry = struct.pack("<BQ", 0xFD, expiry_ms)  # 0xFD + 64-bit little-endian

value_type = 0  # e.g., string
packed_type = struct.pack("B", value_type)
