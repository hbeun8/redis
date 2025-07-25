
'''
Datastore 
'''

from threading import Lock
from protocol_handler import Bulkstring, Array, Error, Integer, Simplestring

class Datastore:
    def __init__(self, data):
        if hasattr(data, 'data'):
            self.data = data.data
        else:
            self.data = data
        self._data = [data]
        self._lock = Lock()

    # _data is a dict: key: str, value: str, expiry:int, type: int
    def Get(self, data:dict):
        # Lock not required in read-only mode.
        '''
        keys = data.keys()
        key = keys[0]
        self._data
        '''
        print("Data ", data)
        print("_Data ", self._data)
        for entry in self._data:
            for key in entry:
                if key in data:
                    return data[key]
                print(f"Key {key} not found")
        return None

    def Add(self, data:dict):
        with self._lock:
            d_keys = list(self.data.keys())
            key = d_keys[0]
            print('Add Item', key)
            for datastore in self._data:
                if key in datastore.keys():
                    print(f"Key {key} already exists")
                    return data
            self._data.append(data)
            return data

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