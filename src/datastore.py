
from threading import Lock
import time
from random import randint
from collections import deque
from dataclasses import dataclass

@dataclass
class Datastore:
    def __init__(self, datastore: list):
        self._lock = Lock()
        self.datastore = datastore
        self.deque = deque() # we dont really need this.

    def __post_init__(self):
        pass

    def Remove(self, k):
        with self._lock:
            try:
                delattr(self, k)
                return "(integer) 1"
            except AttributeError as e:
                return e

    def Get(self, k):
       try: # v is an array
         v = getattr(self, k)
         if self.isExpired(v):
             delattr(self, k)
             return "(nil)"
         return v[0]
       except Exception as e:
           print("Exception ", e)
           return "-Unknown error: Check server."

    def isExpired(self, v):
        try:
            # ---Validation not performed as performed in the Set Class in the command handler---- #
            if v[1].upper().strip() == "EX":
                return time.time_ns() > int(float(v[2]))* 1e+9
            if v[1].upper().strip() == "PX":
                return time.time_ns() > int(float(v[2]))* 1e+6
            else:
                return False
        except Exception as e:
            return False

    def run_scan(self, delay=0.1):
        try:
            while True:
                time.sleep(delay)
                self.scan()
        except IndexError as e:
            print("Passive Delete Expired Keys:", e)

    def scan(self):
        #for key in (self.keys[i] for i in (randint(0, (len(self.keys) - 1)) for k in range(min(20, round(0.25 * len(self.keys))))) if self.isExpired(getattr(self, self.keys[i]))):
        for key in (list(vars((self)).keys())[i] for i in
                    (randint(0, (len(list(vars((self)).keys())) - 1)) for k in
                     range(min(20, round(0.25 * len(list(vars((self)).keys())))))) if
                    self.isExpired(getattr(self, list(vars((self)).keys())[i]))):
            delattr(self, key)

    def LPUSH(self, k, v):
        if hasattr(self, k):
            self.deque = getattr(self, k)
            for el in v:
                self.deque.appendleft(el)
            setattr(self, k, self.deque)
            length = len(list(self.deque))
            return f"(integer) {length}"
        else:
            self.deque = deque()
            for el in v:
                self.deque.appendleft(el)
            length = len(list(self.deque))
            setattr(self, k, self.deque)
            return f"(integer) {length}"


    def RPUSH(self, k, v):
        if hasattr(self, k):
            self.deque = getattr(self, k)
            for el in v:
                self.deque.append(el)
            setattr(self, k, self.deque)
            length = len(list(self.deque))
            return f"(integer) {length}"
        else:
            self.deque = deque()
            for el in v:
                self.deque.append(el)
            length = len(list(self.deque))
            setattr(self, k, self.deque)
            return f"(integer) {length}"


    def lrange(self, k, start, end):
        if not hasattr(self, k):
            return "(empty array)"
        if end < start:
            return "(empty array)"
        return list(getattr(self, k))[int(start):int(end)]


    def Exists(self, k):
        with self._lock:
            try:
                if hasattr(self, k):
                    return "(integer) 1"
                else:
                    return "(integer) 0"
            except Exception as e:
                return e


    def Add(self, k, v):
        with self._lock:
            try:
                setattr(self, k, v)
                return "OK"
            except Exception as e:
                return e

    def incr(self, k):
        with self._lock:
            try:
                v = getattr(self, k)
                new_v = str(int(v[0]) + 1)
                v[0] = new_v
                setattr(self, k, v)
                return f"(integer) {new_v}"
            except Exception as e:
                return e

    def decr(self, k):
        with self._lock:
            try:
                v = getattr(self, k)
                new_v = str(int(v[0]) - 1)
                v[0] = new_v
                setattr(self, k, v)
                return f"(integer) {new_v}"
            except AttributeError as e:
                return e


    def __str__(self):
        return f"Datastore({self.datastore})"

