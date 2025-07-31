
from threading import Lock
from datetime import datetime, timedelta
import time
from dateutil.parser import parse
from random import randint
import asyncio

class Dict:
    def __init__(self, data: dict):
        self.key = next(iter(data))
        self.value = data[self.key]
        self.expiry_name = list(data.keys())[1]
        if self.expiry_name.upper() == 'PX':
            self.expiry = time.time_ns() + int(float(data[self.expiry_name])) * 1e+6
        elif self.expiry_name.upper() == 'EX':
            self.expiry = time.time_ns() + int(float(data[self.expiry_name])) * 1e+9
        else:
            self.expiry = None
        self.type = data["type"] if "type" in data else None
        self.s = f"{self.value}:{self.expiry}:{self.type}"
        self.u_s = data
        self.curr = datetime.now()
        self.keys = data.keys()

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

    def Get_wo_expiry(self, k):
        # Lock not required in read-only mode.
        try:
            v = getattr(self, k)
            sep = v.find(":")
            return v[:sep]
        except AttributeError:
            return "(nil)"

    def Get(self, k):
       # if the key is expired
       try:
           v = getattr(self, k)
           if self.isExpired(v):
               delattr(self, k)
               return "(nil)"
           else:
               sep = v.find(":")
               return v[:sep]
       except AttributeError as e:
           return f"-Err: {e}"

    def isExpired(self, v):
        try:
            sep_1 = v.find(":")+1
            sep_2 = v[sep_1:].find(":")
            expiry = v[sep_1:sep_1+sep_2]
            if expiry == 'None':
                return False
            if isinstance(expiry, (str, int, float)):
                return time.time_ns() > int(float(expiry))
        except Exception as e:
            return f"isExpired: {e}"
    def run_scan(self, delay=0.1):
        try:
            while True:
                time.sleep(delay)
                self.scan()
        except IndexError as e:
            print("Passive Delete Expired Keys:", e)

    def scan(self):
        for key in (self.keys[i] for i in (randint(0, (len(self.keys) - 1)) for k in range(min(20, round(0.25 * len(self.keys)))))):
            delattr(self, key)

    def Exists(self, k):
        with self._lock:
            if hasattr(self, k):
                return "(integer) 1"
            else:
                return "(integer) 0"

    def set_new_expiry_ex(self, k, new_expiry):
        try:
            v = getattr(self, k)
            new_v = self.build_new_v_ex(v, new_expiry)
            self.Add(k, new_v) # override
        except AttributeError:
            return "(nil)"

    def set_new_expiry_px(self, k, new_expiry):
        try:
            v = getattr(self, k)
            new_v = self.build_new_v_px(v, new_expiry)
            self.Add(k, new_v) # override
        except AttributeError:
            return "(nil)"

    def build_new_v_ex(self, v, new_expiry):
        sep_1 = v.find(":")+1
        sep_2 = v[sep_1:].find(":")
        expiry = v[sep_1:sep_1+sep_2]
        new_expiry_s = time.time_ns() + new_expiry*1e+9 # if seconds
        v.replace(expiry, str(new_expiry_s))
        return v

    def build_new_v_px(self, v, new_expiry):
        sep_1 = v.find(":")+1
        sep_2 = v[sep_1:].find(":")
        expiry = v[sep_1:sep_1+sep_2]
        new_expiry_mils = time.time_ns() + new_expiry * 1e+6 # if milliseconds
        new_expiry_mics = time.time_ns() + new_expiry * 1000 # if microseconds
        v.replace(expiry, str(new_expiry_mils))
        return v

    def AddEX(self, k, v):
        with self._lock:
            try:
                if hasattr(self, k):
                    v = self.Get(k)
                    expiry_nano = self.set_new_expiry_ex(k, v) # takes v which has expiry in seconds and sets
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

    def AddPX(self, k, v):
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

    def Add(self, k, v):
        with self._lock:
            try:
                if hasattr(self, k):
                    setattr(self, k, v)
                    pass #return "(already exists)" # we never reach this!
                if v is None:
                    return "-ERR wrong number of arguments for 'set' command"
                if v is not None: # catchall
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

