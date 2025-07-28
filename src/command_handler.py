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
        case "CONFIG":
            return _handle_config()
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
            return _handle_lpush(datastore, persister)
        case "LRANGE":
            return _handle_lrange(command, datastore)
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
            return _handle_sync(datastore)
        case _:
            return _handle_unrecognised_command(command)

def _handle_incr(data, persister):
    print(data)
    return cache.incr(data)

def _handle_decr(data, persister):
    return cache.decr(data)

def _handle_exists(datastore):
    if cache.Add(datastore) == "(already exists)":
        return "(integer) 1"
    else:
        return "(integer) 0"

def _handle_lrange(datastore):
    #datastore {arr: start, 'end', end}
    try:
        arr_name = datastore.keys[0]
        start = datastore.keys[1]
        arr = datastore[arr_name]
        end = datastore.keys[2]
        return arr[start:end]
    except Exception:
        return "(empty) {empty)"

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

def _handle_lpush(datastore, persister):
    # {arr: values, expiry: none, type: none}
    if _handle_exists(datastore) == "(integer) 1":
        arr = _handle_get(datastore)
        ds_key = datastore.key
        temp_arr = []
        temp_arr.insert(0, datastore[ds_key])
        for _ in range(len(arr)):
                temp_arr.append(arr[_])
        datastore = {ds_key: temp_arr, "Expiry": "None"}
        list = e.ladd(cache.Add(datastore))  # cache.add and e.ladd returns array of datastore and then a list
        if list:
            return f'integer (len(list))'
        else:
            return "-Error"
    else: # new arr
        ds_key = datastore.key
        arr = [datastore[ds_key]]
        ds = Datastore({ds_key: arr, "Expiry": "None"})
        if ds:
            for key in ds.keys():
                if e.ladd(cache.Add(datastore)):  # cache.add and e.ladd returns array of datastore
                    return f'integer (len(temp_arr))'
        else:
            return "-Error"

def _handle_rpush(datastore, persister):
    # {arr: values, expiry: none, type: none}
    if _handle_exists(datastore):
        arr = list(_handle_get(datastore))
        ds_key = datastore.key
        temp_arr = []
        temp_arr.insert(0, datastore[ds_key])
        for _ in range(len(arr)):
                temp_arr.append(arr[_])
        ds = Datastore({ds_key: temp_arr, "Expiry": "None"})
        if ds:
            for key in ds.keys():
                if e.ladd(cache.Add(datastore)):  # cache.add and e.ladd returns array of datastore
                    return f'integer (len(temp_arr))'
        else:
            return "-Error"
    else: # new arrr
        ds_key = datastore.key
        arr = [datastore[ds_key]]
        ds = Datastore({ds_key: arr, "Expiry": "None"})
        if ds:
            for key in ds.keys():
                if e.ladd(cache.Add(datastore)):  # cache.add and e.ladd returns array of datastore
                    return f'integer (len(temp_arr))'
        else:
            return "-Error"

def _handle_config():
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
    components = f"*{len(string)}\r\n"
    for element in string:
        components += f"${len(element)}\r\n{element}\r\n"
    return components

def _handle_del(self, datastore, persister):
    _handle_get(datastore)

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
