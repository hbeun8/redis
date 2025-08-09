from typing_extensions import dataclass_transform

from datastore import Datastore, Dict
from protocol_handler import Parser, Bulkstring, Array, Error, Integer, Simplestring
#from multiprocessing import Process
import threading
#from persistence import AppendOnlyPersister, restore_from_file

'create an instance of Datastore. They have to be not None'
cache = Datastore({"key": "value", "Expiry": "value"})
#persister = AppendOnlyPersister("log.aof")

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

def _handle_del(command, datastore, persister):
    # first check if it already exists
    k = datastore.key
    #v = datastore.s
    if cache.Exists(k) == "(integer) 1":
        cache.Remove(k)
        return "(integer) 1"
    else:
        return "(integer) 0"

def _handle_incr(command, datastore, persister):
    k = datastore.key
    v = datastore.s
    return cache.incr(k)

def _handle_decr(command, datastore, persister):
    k = datastore.key
    v = datastore.s
    return cache.decr(k)

def _handle_exists(command, datastore, persister):
    try:
        k = datastore.key
        if k == "" or k is None:
            return "Err wrong number of arguments for 'exists' command"
        return cache.Exists(k)
    except (AttributeError, TypeError) as e:
        return "Err wrong number of arguments for 'exists' command"

def _handle_lrange(command, datastore, persister):
    #datastore {key: <arr_name>, start: <start>, end: <end>}
    result = cache.lrange(datastore.lrange_key, datastore.start, datastore.end)
    return result

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

def _handle_lpush(command, datastore, persister):
    return cache.LPUSH(datastore.key, datastore.value)

def _handle_rpush(command, datastore, persister):
    return cache.RPUSH(datastore.key, datastore.value)


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
    return f"-ERR unknown command {command}"

def _handle_set(command, datastore, persister):
    try:
        k = datastore.key
        v = datastore.s
        cache.Add(k, v) # cache.add returns array of datastore
        return 'OK'
    except AttributeError as ex:
        return f"-Error: {ex}"

def _handle_get(command, datastore, persister):
    try:
        k = datastore.key
        if cache.Get(k) =="(nil)":
            pass#persister.log_command(command, resp_encoder_get("nil")) # synthesize delete for persister in case of expired keys
        return cache.Get(k) # returns array of datastore and then returns key value.
    except Exception as ex:
        return f"-Error: {ex}"


def _handle_sync(command, datastore, persister):
    if datastore:
        for key in datastore.keys():
            result = cache.Get(datastore) # returns array of datastore
            return result
    else:
        return "Key not found"
