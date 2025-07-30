
from threading import Lock


class Dict:
    def __init__(self, data: dict):
        self.key = next(iter(data))
        self.value = data[self.key]
        self.expiry = data["Expiry"] if "Expiry" in data else None
        self.type = data["type"] if "type" in data else None
        self.s = f"{self.value}:{self.expiry}:{self.type}"
        self.u_s = data

class Datastore:
    def __init__(self, data: dict):
        self._lock = Lock()

    def Remove(self, k):
        with self._lock:
            try:
                delattr(self, k)
                return "(integer) 1"
            except AttributeError:
                return ""

    def Get(self, k):
        # Lock not required in read-only mode.
        try:
            v = getattr(self, k)
            return v
        except AttributeError:
            return "(nil)"

    def Add(self, k, v):
        with self._lock:
            try:
                if hasattr(self, k):
                    return "(already exists)" # we never reach this!
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

    def keys(self):
        return list(self.data)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __str__(self):
        return f"Datastore({self.key}  {self.value})"
