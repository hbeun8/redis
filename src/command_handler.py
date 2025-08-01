from typing_extensions import dataclass_transform

from datastore import Datastore, Dict
from expiry import Expiry
from protocol_handler import Parser, Bulkstring, Array, Error, Integer, Simplestring
import threading
import asyncio
from persistence import AppendOnlyPersister, restore_from_file

'create an instance of Datastore and Expiry. They have to be not None'
cache = Datastore({"key": "value", "Expiry": "value"})
persister = AppendOnlyPersister("log.aof")
#***
scan = threading.Thread(target=cache.run_scan, args=(), daemon=True)
scan.start()
#***

def handle_command(command, datastore, persister=None):
    match command:
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
            '''
            exp = datastore.expiry_name
            if exp == "PX" or exp == "px":
                return _handle_set_px(datastore, persister)
            if exp == "EX" or exp == "ex":
                return _handle_set_ex(datastore, persister)
            '''
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
            return "-Err wrong number of arguments for 'exists' command"
        return cache.Exists(k)
    except Exception as e:
        return "-Err wrong number of arguments for 'exists' command"

def _handle_lrange(command, datastore, persister):
    #datastore {arr: start, 'end': end}
    k = datastore.key
    v = datastore.s
    try:
        arr_name = datastore.keys[0]
        start = datastore.keys[1]
        arr = datastore[arr_name]
        end = datastore.keys[2]
        return arr[start:end]
    except Exception:
        return "(empty) {empty)"

'''
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
'''

def resp_encoder_get(data):

    if len(data) == 0:
        return ""
    data = " ".join(data)
    if data == [None]:
        '*-1\r\n'
    if data is None:
        return ""
    return f"*1\r\n${len(data)}\r\n{data}\r\n"

def _handle_ping(command, datastore, persister):
    try:
        return "PONG"

    except Exception as e:
        return f"-ERROR {str(e)}\r\n"

def _handle_lpush(command, datastore, persister):
    # {arr: values, expiry: none, type: none}
    if _handle_exists(datastore) == "(integer) 1":
        arr = _handle_get(datastore)
        ds_key = datastore.key
        temp_arr = []
        temp_arr.insert(0, datastore[ds_key])
        for _ in range(len(arr)):
                temp_arr.append(arr[_])
        datastore = {ds_key: temp_arr, "Expiry": "None"}
        list = cache.Add(datastore)  # cache.add and e.ladd returns array of datastore and then a list
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
                if cache.Add(datastore):  # cache.add and e.ladd returns array of datastore
                    return f'integer (len(temp_arr))'
        else:
            return "-Error"

def _handle_rpush(command, datastore, persister):
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
    components = f"*{len(string)}\r\n"
    for element in string:
        components += f"${len(element)}\r\n{element}\r\n"
    return components

def _handle_unrecognised_command(command, datastore, persister):
    return f"-ERR unknown command {command}"

def _handle_set(command, datastore, persister):
    try:
        k = datastore.key
        v = datastore.s
        cache.Add(k, v) # cache.add and e.ladd returns array of datastore
        return 'OK'
    except Exception as ex:
        return f"-Error: {ex}"

def _handle_set_ex(command, datastore, persister):
    try:
        k = datastore.key
        v = datastore.s
        cache.AddEX(k, v) # cache.add and e.ladd returns array of datastore
        return 'OK'
    except Exception as ex:
        return f"-Error: {ex}"

def _handle_set_px(command, datastore, persister):
    try:
        k = datastore.key
        v = datastore.s
        cache.AddPX(k, v) # cache.add and e.ladd returns array of datastore
        return 'OK'
    except Exception as ex:
        return f"-Error: {ex}"


def _handle_get(command, datastore, persister):
    try:
        k = datastore.key
        if cache.Get(k) =="(nil)"
            persister.log_command(command, resp_encoder_get("nil")) # synthesize delete for persister in case of expired keys
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
