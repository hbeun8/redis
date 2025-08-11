from datastore import Datastore
#from multiprocessing import Process
import threading
from dataclasses import dataclass
'create an instance of Datastore. They have to be not None'
cache = Datastore(["key", "value", "EX", "100"])

#*** Background Scan to remove expired keys
scan = threading.Thread(target=cache.run_scan, args=(), daemon=True)
scan.start()
#***

def handle_command(command, datastore, persister=None):

    match command.upper():
        case "CONFIG":
            return _handle_config(command, datastore, persister)
        case "DECR":
            return _handle_decr(command, datastore, persister)
        case "DEL":
            return _handle_del(command, datastore, persister)
        case "ECHO":
            return "" # handled in the connection_handler as part of redis min connection requirements.
        case "EXISTS":
            return _handle_exists(command, datastore, persister)
        case "INCR":
            return _handle_incr(command, datastore, persister)
        case "LPUSH":
            return _handle_lpush(command, datastore, persister)
        case "LRANGE":
            return _handle_lrange(command, datastore, persister)
        case "PING":
            return _handle_ping(command, datastore, persister)
        case "RPUSH":
            return _handle_rpush(command, datastore, persister)
        case "SET":
            return _handle_set(command, datastore, persister)
        case "GET":
            return _handle_get(command, datastore, persister)
        # for replication
        case "SYNC":
            return _handle_sync(command, datastore, persister)
        case _:
            return _handle_unrecognised_command(command, datastore, persister)

@dataclass
class Del(Datastore):
    datastore: list

    def __post_init__(self):
        if self.datastore is None or len(self.datastore) == 0:
            raise ValueError("-ERR wrong number of arguments for 'del' command")
        if self.datastore == ['']:
            raise ValueError("-ERR wrong number of arguments for 'del' command")
        else:
            self.key = self.datastore[0]
        if len(self.datastore) == 2:
            if self.datastore[1] == "":
                raise ValueError("-ERR wrong number of arguments for 'del' command")
            else:
                self.value = self.datastore[1]
        if len(self.datastore) == 3:
            raise ValueError("-ERR wrong number of arguments for 'del' command")

    def run_del(self):
        k = self.datastore[0]
        if cache.Exists(k) == "(integer) 1":
            cache.Remove(k)
            return "(integer) 1"
        else:
            return "(integer) 0"

def _handle_del(command, datastore, persister):
    # first check if it already exists
    try:
        result = Del(datastore)
        return result.run_del()
    except ValueError as e:
        return e

@dataclass
class Incr(Datastore):
    datastore: list

    def __post_init__(self):
        if self.datastore is None or len(self.datastore) == 0:
            raise ValueError("-ERR wrong number of arguments for 'incr' command")
        if self.datastore == ['']:
            raise ValueError("-ERR wrong number of arguments for 'incr' command")
        else:
            self.key = self.datastore[0]
        if len(self.datastore) == 2:
            if self.datastore[1] == "":
                raise ValueError('-ERR value is not an integer or out of range')
            else:
                self.value = self.datastore[1]
        if len(self.datastore) > 3:
            raise ValueError("-ERR wrong number of arguments for 'incr' command")

    def run_incr(self):
        return cache.incr(self.datastore[0])

def _handle_incr(command, datastore, persister):
    try:
        results = Incr(datastore)
        return results.run_incr()
    except ValueError as e:
        return e

@dataclass
class Decr(Datastore):
    datastore: list

    def __post_init__(self):
        if self.datastore is None or len(self.datastore) == 0:
            raise ValueError("-ERR wrong number of arguments for 'decr' command")
        if self.datastore == ['']:
            raise ValueError("-ERR wrong number of arguments for 'decr' command")
        else:
            self.key = self.datastore[0]
        if len(self.datastore) == 2:
            if self.datastore == ["", ""]:
                raise ValueError("-ERR wrong number of arguments for 'decr' command")
            elif self.datastore[1] == "":
                raise ValueError('-ERR value is not an integer or out of range')
            else:
                self.value = self.datastore[1]
        if len(self.datastore) > 3:
            raise ValueError("-ERR wrong number of arguments for 'Decr' command")

    def run_decr(self):
        return cache.decr(self.datastore[0])


def _handle_decr(command, datastore, persister):
    try:
        results = Decr(datastore)
        return results.run_decr()
    except ValueError as e:
        return e

@dataclass
class Exists(Datastore):
    datastore: list

    def __post_init__(self):
        if self.datastore is None or len(self.datastore) == 0:
            raise ValueError("-ERR wrong number of arguments for 'exists' command")
        if self.datastore == ['']:
            raise ValueError("-ERR wrong number of arguments for 'exists' command")
        else:
            self.key = self.datastore[0]
        if len(self.datastore) == 2:
            if self.datastore[1] == "":
                raise ValueError("-ERR wrong number of arguments for 'exists' command")
            else:
                self.value = self.datastore[1]
        if len(self.datastore) == 3:
            raise ValueError("-ERR wrong number of arguments for 'exists' command")
        if len(self.datastore) == 4:
            if self.datastore[2].upper != "EX" or self.datastore[2].upper != "PX":
                raise ValueError("-ERR syntax error")
            if self.datastore[3] == "":
                raise ValueError("-ERR syntax error")
        if len(self.datastore) > 4:
            raise ValueError("-ERR syntax error")

    def run_exists(self):
        return cache.Exists(self.key)

def _handle_exists(command, datastore, persister):
    try:
        results = Exists(datastore)
        return results.run_exists()
    except ValueError as e:
        return e

@dataclass
class Lrange(Datastore):
    datastore: list

    def __post_init__(self):
        if self.datastore is None or len(self.datastore) == 0:
            raise ValueError("-ERR wrong number of arguments for 'lrange' command")
        if self.datastore == ['']:
            raise ValueError("-ERR wrong number of arguments for 'lrange' command")
        if len(self.datastore) == 2:
            raise ValueError("-ERR wrong number of arguments for 'lrange' command")
        if len(self.datastore) == 3:
            if self.datastore[2] == "":
                raise ValueError("-ERR wrong number of arguments for 'lrange' command")
        if len(self.datastore) > 4:
            raise ValueError("-ERR wrong number of arguments for 'lrange' command")

    def run_lrange(self):
        return cache.lrange(self.datastore[0], self.datastore[1], self.datastore[2])

def _handle_lrange(command, datastore, persister):
   try:
        results = Lrange(datastore)
        return results.run_lrange()
   except ValueError as e:
       return e

def resp_encoder_get(data):
    try:
        if data is None:
            return ""
        if data == [None]:
            return '*-1\r\n'
        if len(data) == 0:
            return ""
        data = " ".join(data)
        return f"*1\r\n${len(data)}\r\n{data}\r\n"
    except TypeError as e:
        print(e)

def _handle_ping(command, datastore, persister):
    try:
        return "PONG"

    except Exception as e:
        return f"-ERROR {str(e)}\r\n"

@dataclass
class Lpush(Datastore):
    datastore: list

    def __post_init__(self):
        if self.datastore is None or len(self.datastore) == 0:
            raise ValueError("-ERR wrong number of arguments for 'lpush' command")
        if self.datastore == ['']:
            raise ValueError("-ERR wrong number of arguments for 'lpush' command")
        else:
            self.key = self.datastore[0]
        if len(self.datastore) == 2:
            if self.datastore[1] == "":
                raise ValueError("-ERR wrong number of arguments for 'lpush' command")
            else:
                self.value = self.datastore[1]

    def run_lpush(self):
        return cache.LPUSH(self.datastore[0], self.datastore[1:])

def _handle_lpush(command, datastore, persister):
    try:
        result = Lpush(datastore)
        return result.run_lpush()
    except ValueError as e:
        return e


@dataclass
class Rpush(Datastore):
    datastore: list

    def __post_init__(self):
        if self.datastore is None or len(self.datastore) == 0:
            raise ValueError("-ERR wrong number of arguments for 'rpush' command")
        if self.datastore == ['']:
            raise ValueError("-ERR wrong number of arguments for 'rpush' command")
        else:
            self.key = self.datastore[0]
        if len(self.datastore) == 2:
            if self.datastore[1] == "":
                raise ValueError("-ERR wrong number of arguments for 'rpush' command")
            else:
                self.value = self.datastore[1]

    def run_rpush(self):
        return cache.RPUSH(self.datastore[0], self.datastore[1:])

def _handle_rpush(command, datastore, persister):
    try:
        result = Rpush(datastore)
        return result.run_rpush()
    except ValueError as e:
        return e

def _handle_config(command, datastore, persister):
    string = ["List of supported commands:",
              "COMMAND: ",
              "CONFIG ",
              "DECR: ",
              "DEL:",
              "ECHO",
              "EXISTS",
              "INCR",
              "LPUSH",
              "LRANGE",
              "PING",
              "RPUSH",
              ]
    length = len(string)
    components = f"*{len(string)}\n"
    for element in string:
        components += f"${len(element)}\n{element}\n"
    return components

def _handle_unrecognised_command(command, datastore, persister):
    return f"-ERR unknown command '{command}', with args beginning with: {" ".join(datastore).strip()}"

@dataclass
class Set(Datastore):
    datastore: list

    def __post_init__(self):
        if self.datastore is None or len(self.datastore) == 0:
            raise ValueError("-ERR wrong number of arguments for 'set' command")
        if self.datastore == ['']:
            raise ValueError("-ERR wrong number of arguments for 'set' command")
        else:
            self.key = self.datastore[0]
        if len(self.datastore) == 2:
            if self.datastore[1] == "":
                raise ValueError("-ERR wrong number of arguments for 'set' command")
            else:
                self.value = self.datastore[1:]  # not erequired
                print(self.value) # not requiered
        if len(self.datastore) == 3:
            raise ValueError("-ERR wrong number of arguments for 'set' command")
        if len(self.datastore) == 4:
            if self.datastore[2].upper().strip() not in ["EX", "PX"]:
                raise ValueError("-ERR syntax error")
            if self.datastore[3] == "":
                raise ValueError("-ERR syntax error")
        if len(self.datastore) > 4:
            raise ValueError("-ERR syntax error")

    def run_set(self):
        print(self.datastore[0])
        print(self.datastore[1:])
        return cache.Add(self.datastore[0], self.datastore[1:])

def _handle_set(command, datastore, persister):
    try:
        result = Set(datastore)
        print(result)
        return result.run_set()
    except ValueError as e:
        return e

@dataclass
class Get(Datastore):
    datastore: list

    def __post_init__(self):
        if self.datastore is None or len(self.datastore) == 0:
            raise ValueError("-ERR wrong number of arguments for 'get' command")
        if self.datastore == [""]:
            raise ValueError("-ERR wrong number of arguments for 'get' command")
        else:
            self.key = self.datastore[0]
    def run_get(self):
        return cache.Get(self.datastore[0])

def _handle_get(command, datastore, persister):
    try:
        result = Get(datastore)
        print(result)
        return result.run_get()
    except ValueError as e:
        return e


def _handle_sync(command, datastore, persister):
    if datastore:
        for key in datastore.keys():
            result = cache.Get(datastore) # returns array of datastore
            return result
    else:
        return "Key not found"
