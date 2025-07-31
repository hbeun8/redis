from typing_extensions import dataclass_transform

from datastore import Datastore, Dict
from expiry import Expiry
from protocol_handler import Parser, Bulkstring, Array, Error, Integer, Simplestring
import threading
import asyncio

def start_async_loop_in_thread(cache):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(asyncio.to_thread(cache.run_scan))
    loop.run_forever()

'create an instance of Datastore and Expiry. They have to be not None'
cache = Datastore({"key": "value", "Expiry": "value"})
e = Expiry({"key": "value", "Expiry": "value"})

#***
#threading.Thread(target=start_async_loop_in_thread, args=(cache,), daemon=True).start()
#***
def handle_command(command, dictionary, persister=None):

    datastore = Dict(dictionary)

    match command:
        case "CONFIG":
            return _handle_config()
        case "DECR":
            return _handle_decr(datastore, persister)
        case "DEL":
            return _handle_del(datastore, persister)
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
            '''
            exp = datastore.expiry_name
            if exp == "PX" or exp == "px":
                return _handle_set_px(datastore, persister)
            if exp == "EX" or exp == "ex":
                return _handle_set_ex(datastore, persister)
            '''
            return _handle_set(datastore, persister)
        case "GET":
            return _handle_get(datastore)
        # for replication
        case "SYNC":
            return _handle_sync(datastore)
        case _:
            return _handle_unrecognised_command(command)

def _handle_del(datastore, persister):
    # first check if it already exists
    k = datastore.key
    #v = datastore.s
    if cache.Exists(k) == "(integer) 1":
        cache.Remove(k)
        return "(integer) 1"
    else:
        return "(integer) 0"

def _handle_incr(datastore, persister):
    k = datastore.key
    v = datastore.s
    return cache.incr(k)

def _handle_decr(datastore, persister):
    k = datastore.key
    v = datastore.s
    return cache.decr(k)

def _handle_exists(datastore):
    try:
        k = datastore.key
        if k == "" or k is None:
            return "-Err wrong number of arguments for 'exists' command"
        return cache.Exists(k)
    except Exception as e:
        return "-Err wrong number of arguments for 'exists' command"

def _handle_lrange(datastore):
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

def resp_encoder_get(data):
    if isinstance(data, list):
        if len(data) == 0:
            return ""
        data = " ".join(data)
        if data == [None]:
            '*-1\r\n'
    if data is None:
        return ""
    return f"*1\r\n${len(data)}\r\n{data}\r\n"

def _handle_ping(datastore):
    try:
        return "PONG"

    except Exception as e:
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

def _handle_unrecognised_command(command: str):
    return f"-ERR unknown command {command}"

def _handle_set(datastore, persister):
    try:
        k = datastore.key
        v = datastore.s
        cache.Add(k, v) # cache.add and e.ladd returns array of datastore
        return 'OK'
    except Exception as ex:
        return f"-Error: {ex}"

def _handle_set_ex(datastore, persister):
    try:
        k = datastore.key
        v = datastore.s
        cache.AddEX(k, v) # cache.add and e.ladd returns array of datastore
        return 'OK'
    except Exception as ex:
        return f"-Error: {ex}"

def _handle_set_px(datastore, persister):
    try:
        k = datastore.key
        v = datastore.s
        cache.AddPX(k, v) # cache.add and e.ladd returns array of datastore
        return 'OK'
    except Exception as ex:
        return f"-Error: {ex}"


def _handle_get(datastore):
    try:
        k = datastore.key
        return e.get_value(cache.Get(k)) # returns array of datastore and then returns key value.
    except Exception as ex:
        return f"-Error: {ex}"


def _handle_sync(datastore):
    if datastore:
        for key in datastore.keys():
            result = e.get_ds(cache.Get(datastore)) # returns array of datastore
            return result
    else:
        return "Key not found"
