
from threading import Lock
from datetime import datetime, timedelta
import time
from random import randint
from collections import deque
from protocol_handler import Bulkstring

class Dict:
    def __init__(self, data: dict):
        self.key = next(iter(data.keys())) if data else None
        try:
            self.value = data[self.key]
        except AttributeError as e:
            self.value = None
        try:
            self.lrange_key = data["lrange_key"]
        except (TypeError, AttributeError, KeyError):
            self.lrange_key = None
        try:
            self.expiry_name = list(data.keys())[1]
        except (AttributeError, IndexError):
            self.expiry_name = None
        try:
            if self.expiry_name.upper() == 'PX':
                self.expiry = time.time_ns() + int(float(data[self.expiry_name])) * 1e+6
            elif self.expiry_name.upper() == 'EX':
                self.expiry = time.time_ns() + int(float(data[self.expiry_name])) * 1e+9
        except (TypeError, AttributeError, IndexError, ValueError):
            self.expiry =""
        self.type = data["type"] if "type" in data else None
        try:
            self.s = f"{self.value}:{self.expiry}:{self.type}"
        except AttributeError: # in case there is no expiries
            self.s = f"{self.value}:{self.type}"
        self.u_s = data
        self.curr = datetime.now()
        try:
            self.keys = data.keys()
            self.start =  data["start"]
            self.end = data["end"]
        except (AttributeError,TypeError, IndexError, KeyError) as e:
            self.start = None
            self.end = None
            self.keys = None

    def __dict__(self):
        print("data: ", self.u_s)

    def __iter__(self, data):
        self.data = data
        self.index = len(data)

    def __next__(self):
        if self.index == 0:
            raise StopIteration
        self.index = self.index - 1
        return self.data[self.index]


class Datastore:
    def __init__(self, data: dict):
        self._lock = Lock()
        self.keys = list(vars(self).keys()) # or just use list(dir(self))
        self.deque = deque()

    def Remove(self, k):
        with self._lock:
            try:
                delattr(self, k)
                return "(integer) 1"
            except AttributeError as e:
                return f"-Error removing key: {e}"

    def Get_wo_expiry(self, k):
        # Lock not required in read-only mode.
        try:
            v = getattr(self, k)
            sep = v.find(":")
            return v[:sep]
        except AttributeError:
            return "(nil)"

    def Get(self, k, expiry_name=None):
       try:
           v = getattr(self, k)
           if expiry_name is None:
               return v[:v.find(":")]
           if self.isExpired(v):
               delattr(self, k)
               return "(nil)"
       except Exception as e:
           return f"-Err: {e}"

    def isExpired(self, v):
        try:
            sep_1 = v.find(":")+1
            sep_2 = v[sep_1:].find(":")
            expiry = v[sep_1:sep_1+sep_2]
            if expiry == 'None' or expiry == '' or expiry is None:
                return Exception
            #if isinstance(expiry, (str, int, float)):
            return time.time_ns() > int(float(expiry))
        except Exception as e:
            return f"Expiry invalid {e}"

    def run_scan(self, delay=0.1):
        try:
            while True:
                time.sleep(delay)
                self.scan()
        except IndexError as e:
            print("Passive Delete Expired Keys:", e)

    def scan(self):
        for key in (self.keys[i] for i in (randint(0, (len(self.keys) - 1)) for k in range(min(20, round(0.25 * len(self.keys))))) if self.isExpired(getattr(self, self.keys[i]))):
            delattr(self, key)

    def LPUSH(self, k, v):
        # existing key
        if hasattr(self, k):
            #deque_v = getattr(self, k)
            for el in v:
                self.deque.appendleft(el.data)
            setattr(self, k, self.deque)
            length = len(list(self.deque))
            return f"(integer) {length}"
        else:
            for el in v:
                self.deque.appendleft(el.data)
            length = len(list(self.deque))
            setattr(self, k, list(self.deque))
            return f"(integer) {length}"


    def RPUSH(self, k, v):
        # existing key
        if hasattr(self, k):
            #deque_v = getattr(self, k)
            for el in v:
                self.deque.append(el.data)
            setattr(self, k, self.deque)
            length = len(list(self.deque))
            return f"(integer) {length}"
        else:
            for el in v:
                self.deque.append(el.data)
            length = len(list(self.deque))
            setattr(self, k, list(self.deque))
            return f"(integer) {length}"


    def lrange(self, k, start, end):
        if not hasattr(self, k):
            return f"(empty array)"
        s_v = getattr(self, k)
        return list(s_v)[int(start):int(end)]


    def Exists(self, k):
        with self._lock:
            try:
                if hasattr(self, k):
                    return "(integer) 1"
                else:
                    return "(integer) 0"
            except Exception as e:
                return f"-Err: {e}"


    def build_new_v_ex(self, v, new_expiry):
        sep_1 = v.find(":")+1
        sep_2 = v[sep_1:].find(":")
        expiry = v[sep_1:sep_1+sep_2]
        new_expiry_s = time.time_ns() + new_expiry*1e+9 # if seconds
        v.replace(expiry, str(new_expiry_s))
        return v

    def Add(self, k, v, expiry_name=None):
        with self._lock:
            try:
                if expiry_name is not None:
                    if isinstance(self.expiry, int):
                        pass
            except Exception as e:
                return f"-Err missing expiry: {e}"
            try:
                if k == "" or k is None:
                    return "-ERR wrong number of arguments for 'set' command"
                if hasattr(self, k):
                    setattr(self, k, v)
                    pass #return "(already exists)" # we never reach this!
                if v is None or "":
                    return "-ERR wrong number of arguments for 'set' command"
                if v is not None: # catchall
                    setattr(self, k, v)
                    return "+OK"
                if v == "None:None:None" or v == "" or k == "" or k is None or k == "":
                    return "-ERR wrong number of arguments for 'set' command"
            except Exception as e:
                return f"-ERR {e}"

    def incr(self, k):
        with self._lock:
            try:
                if k is None or "":
                    return "-ERR wrong number of arguments for 'incr' command"
                if not hasattr(self, k):
                    return "-Error: key not found"
                s = getattr(self, k)
                sep = s.find(":")
                v = str(s[:sep])
                if isinstance(int(v), int):
                    new_v = str(int(v) + 1)
                    new_s = new_v + s[sep:]
                    setattr(self, k, new_s)
                    return f"(integer) {new_v}"
                return "-Error: Key not int"
            except (AttributeError, ValueError, IndexError) as e:
                return f"(error) ERR value is not an integer or out of range"

    def decr(self, k):
        with self._lock:
            try:
                if not hasattr(self, k):
                    return "-Error: key not found"
                s = getattr(self, k)
                sep = s.find(":")
                v = str(s[:sep])
                if not isinstance(int(v), int):
                    return "-Error: Key not int"
                new_v = str(int(v) - 1)
                new_s = new_v + s[sep:]
                setattr(self, k, new_s)
                return f"(integer) {new_v}"
            except AttributeError as e:
                return f"-Err {e}"

    def keys(self):
        return list(self.data)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __str__(self):
        return f"Datastore({self.key}  {self.value})"

