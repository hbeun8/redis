
'''
Datastore 
'''

from threading import Lock
from protocol_handler import Bulkstring, Array, Error, Integer, Simplestring

class Datastore:
    def __init__(self, data:dict):
        self.all_keys = []
        if hasattr(data, 'data'):
            self.data = data.data
        else:
            self.data = data
        self._data = []
        self._lock = Lock()
        self.keys = list(data.keys())
        try:
            self.key = self.keys[0]
        except IndexError:
            return "-Error"
        self.all_keys.append(self.key)

    # _data is a dict: key: str, value: str, expiry:int, type: int
    def log(self, data):
        print("(logged)")

    def Remove(self, data):
        self._data.remove(data)

    def Get(self, data):
        # Lock not required in read-only mode.
        keys = list(data.keys())
        key = keys[0]
        for datastore in self._data:
            if key in datastore.keys():
                return datastore[key]
            else:
                print(f"Key {key} not found")
        return "(nil)"

    def Add(self, data:dict):
        with self._lock:   #
            keys = list(data.keys())
            key = keys[0]
            for datastore in self._data:
                if key in datastore.keys():
                    print(f"Key {key} already exists")
                    return "(already exists)"
            self._data.append(data)
            return data

    def incr(self, data:dict):
        try: #with self._lock:
            if self.Add(data) == "(already exists)":
                v = 0
                key = data.key
                print("incr key", key)
                v = str(self.Get(key) + 1)
                print(v)
                return f"(integer) {v}"
        except Exception as e:
            print("INCR exception", e)
            return e

    def decr(self, data):
        try: #with self._lock:
            v = 0
            def _decr(data):
                key = list(data.key())[0]
                v = str(int(key) - 1)
                return v
            map(_decr,self.data)
            return f"(integer) {v}"

        except Exception as e:
            print("DECR Exception", e)
            return e

    def Len(self):
        return len(self._data)

    def keys(self):
        return self.data.keys()

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

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