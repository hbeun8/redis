
'''
Datastore 
'''
from _ast import While
from asyncio import Queue
from threading import Lock
from dataclasses import dataclass

class Datastore:
    def __init__(self, data: dict):
        self._data = [data]
        self._lock = Lock()
        self._value = data.get("key")
        self._expiry = data.get("del key")

    # _data is a dict: key: str, value: str, expiry:int, type: int
    def Get(self, key):
        # Lock not required in read-only mode.
        return self._data.get('key')

    def Add(self, data):
        with self._lock:
            for key in data.keys():
                if key in self._data:
                    print(f"Key {key} already exists")
                    return data
            self._data.append(data)
            return data
    def Len(self):
        return len(self._data)
    def __str__(self):
        return f"Datastore({self._data})"
'''
import struct

expiry_ms = 1724189999000  # epoch in ms
packed_expiry = struct.pack("<BQ", 0xFD, expiry_ms)  # 0xFD + 64-bit little-endian

value_type = 0  # e.g., string
packed_type = struct.pack("B", value_type)

# Task destructure
@dataclass
class Task:
    task_id: int
    response_queue: Queue
    response: int = 0

# thread doing some work    
while True:
    task = self._queue.get()
    if task is not None:
        task.response = task.val + 2
        task.response_queue.put(task)
        

# Thread sending work
result_queue = Queue()

while True:
    try:
        v = # ... some value to be processed
        processor.process(Task(v, result_queue))
        result = result_queue.get()
        print(result.response)
'''