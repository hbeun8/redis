
from threading import Lock
from datetime import datetime, timedelta
from dateutil.parser import parse
from random import randint
import asyncio

class Dict:
    def __init__(self, data: dict):
        self.key = next(iter(data))
        self.value = data[self.key]
        self.expiry = data["Expiry"] if "Expiry" in data else None
        self.type = data["type"] if "type" in data else None
        self.s = f"{self.value}:{self.expiry}:{self.type}"
        self.u_s = data
        self.curr = datetime.now()

class Datastore:
    def __init__(self, data: dict):
        self._lock = Lock()
        self.keys = list(vars(self).keys())

    def Remove(self, k):
        with self._lock:
            try:
                delattr(self, k)
                return "(integer) 1"
            except AttributeError as e:
                return f"-Error removing key: {e}"

    def Get(self, k):
        # Lock not required in read-only mode.
        try:
            v = getattr(self, k)
            sep = v.find(":")
            return v[:sep]
        except AttributeError:
            return "(nil)"

    def Get_w_Expiry(self, k):
       # if the key is expired
       try:
           v = getattr(self, k)
           if self.isExpired(v):
               return "+OK"
           else:
               return "(nil)"
       except AttributeError:
           return "(nil)"

    def isExpired(self, v):
        sep_1 = v.find(":")+1
        sep_2 = v[sep_1:].find(":")
        expiry = v[sep_1:sep_1+sep_2]
        if isinstance(expiry, (str, int, None)):
            return True
        if isinstance(expiry, datetime):
            return datetime.now() < parse(expiry)

    def run_scan(self, delay=0.1):
        try:
            while True:
                asyncio.sleep(delay)
                self.scan()
        except IndexError as e:
            print("Passive Delete Array", e)

    def scan(self):
        for key in (self.keys[i] for i in (randint(0, (len(self.keys) - 1)) for k in range(min(20, round(0.25 * len(self.keys)))))):
            delattr(self, key)

    def Exists(self, k):
        with self._lock:
            if hasattr(self, k):
                return "(integer) 1"
            else:
                return "(integer) 0"

    def set_new_expiry_px_ex(self, k, new_expiry):
        try:
            v = getattr(self, k)
            new_v = self.build_new_v(v, new_expiry)
            self.Add(k, new_v) # override
        except AttributeError:
            return "(nil)"

    def build_new_v(self, v, new_expiry):
        sep_1 = v.find(":")+1
        sep_2 = v[sep_1:].find(":")
        expiry = v[sep_1:sep_1+sep_2]
        new_expiry = datetime.now() + timedelta(seconds=new_expiry)
        v.replace(expiry, str(new_expiry))
        return v

    def Add(self, k, v):
        with self._lock:
            try:
                if hasattr(self, k):
                    setattr(self, k, v)
                    pass #return "(already exists)" # we never reach this!
                if v is None:
                    return "-ERR wrong number of arguments for 'set' command"
                if v is not None:
                    setattr(self, k, v)
                    return "+OK"
                if v == "None:None:None" or v == "" or k == "" or k is None:
                    return "-ERR wrong number of arguments for 'set' command"
            except Exception as e:
                return f"-ERR {e}"

    def AddX(self, data:dict):
        with self._lock:   #
            try:
                # Light Version
                setattr(self._data, self.key, data)
                return data
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
            except AttributeError as e:
                return f"-Err {e}"

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

    def delete_expired_key(self, k):
        try:
            v = getattr(self, k)
            if self.isExpired(v):
                # set type = 1 and buld new v
                delattr(self, k)
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
