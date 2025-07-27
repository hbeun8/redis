from typing_extensions import dataclass_transform

from datastore import Datastore
from expiry import Expiry
from protocol_handler import parse_frame, Bulkstring, Array, Error, Integer, Simplestring

'create an instance of Datastore and Expiry. They have to be not None'
cache = Datastore({"key": "value", "Expiry": "value"})
e = Expiry({"key": "value", "Expiry": "value"})

def handle_command(command, datastore, persister=None):

    #print("Datastore:", datastore)
    #print("COMMAND FRAME:", command)
    #print("COMMAND TYPE:", type(command))
    #print("COMMAND DATA:", datastore)
    cache.log(command)
    #print("Datastore keys:", datastore.keys())
    #print("Datastore keys:", datastore.values())
    match command:
        case "COMMAND":
            return print("Redis-cli is connected")
        case "CONFIG":
            return _handle_config(command)
        case "DECR":
            return _handle_decr(datastore, persister)
        case "DEL":
            return _handle_del(command, datastore, persister)
        case "ECHO":
            return _handle_echo(datastore)
        case "EXISTS":
            return _handle_exists(datastore)
        case "INCR":
            return _handle_incr(datastore, persister)
        case "LPUSH":
            return _handle_lpush(command, datastore, persister)
        case "LRANGE":
            return _handle_range(command, datastore)
        case "PING":
            return _handle_ping(datastore)
        case "RPUSH":
            return _handle_rpush(command, datastore, persister)
        case "SET":
            return _handle_set(datastore, persister)
        case "GET":
            return _handle_get(datastore)
        # for replication
        case "SYNC":
            return _handle_sync(datastore, persistance)
        case _:
            return _handle_unrecognised_command(command)

def _handle_incr(data, persister):
    return cache.incr(data)

def _handle_decr(data, persister):
    return cache.decr(data)

def _handle_exists(keys):
    keys_data = []
    for _ in keys:
        keys_data.append(_.data)
    #print("keys:", keys_data)
    found_keys = []
    if keys is None or isinstance(keys, dict) or "Err" in keys or len(keys) == 0:
        return "Err"
    for key in keys_data:
        if key in cache.keys():
            found_keys.append(key)
    return Integer(len(found_keys))


def _handle_echo(data):
    try:
        if isinstance(data, str):
            if data == "":
                return "-Err"
            else:
                return data
        if isinstance(data, Array):
            return data.data.data
        if isinstance(data, Bulkstring):
            return data.data

    except Exception as e:
        return "-Err"

def resp_encoder_get(data: str):
    return f"*1\r\n${len(data)}\r\n{data}\r\n"



def _handle_ping(datastore):
    try:
        return "PONG"

    except Exception as e:
        print("Error in _handle_ping:", e)
        return f"-ERROR {str(e)}\r\n"


def _handle_config(datastore):
    return resp_encoder_get("")

def _handle_unrecognised_command(command):
    return ""

def _handle_set(datastore, persister):
    if datastore:
        for key in datastore.keys():
                if e.ladd(cache.Add(datastore)): # cache.add and e.ladd returns array of datastore
                    return 'OK'
    else:
        return "-Error"

def _handle_get(datastore):
    if datastore:
            result = e.get_value(cache.Get(datastore)) # returns array of datastore and then returns key value.
            #print(result)
            return result #resp_encoder_get(result)
    else:
        return "-ERROR"


def _handle_sync(datastore):
    if datastore:
        for key in datastore.keys():
            result = e.get_ds(cache.Get(datastore)) # returns array of datastore
            return result
    else:
        return "Key not found"
