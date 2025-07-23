
from datastore import Datastore
from expiry import Expiry
from protocol_handler import Bulkstring, Array, Error, Integer, Simplestring

'create an instance of Datastore and Expiry. They have to be not None'
cache = Datastore({"key": "value", "Expiry": "value"})
e = Expiry({"key": "value", "Expiry": "value"})
def handle_command(command, datastore, persister=None):
    datastore = datastore.data
    if isinstance(command, Array):
        frameArr = command.data
        command = frameArr[0].data.upper()

        print("COMMAND FRAME:", command)
        print("COMMAND TYPE:", type(command))
        print("COMMAND DATA:", getattr(command, 'data', None))  # Safely prints `.data` if exists
        #print("Datastore keys:", datastore.keys())
        #print("Datastore keys:", datastore.values())
    match command:
        case "CONFIG":
            return _handle_config(command)
        case "DECR":
            return _handle_decr(command, datastore, persister)
        case "DEL":
            return _handle_del(command, datastore, persister)
        case "ECHO":
            return _handle_echo(datastore)
        case "EXISTS":
            return _handle_exists(datastore)
        case "INCR":
            return _handle_incr(command, datastore, persister)
        case "LPUSH":
            return _handle_lpush(command, datastore, persister)
        case "LRANGE":
            return _handle_range(command, datastore)
        case "PING":
            return _handle_ping()
        case "RPUSH":
            return _handle_rpush(command, datastore, persister)
        case "SET":
            return _handle_set(datastore, persister)
        case "GET":
            return _handle_get(datastore)
        case _:
            return _handle_unrecognised_command(command)

def _handle_exists(keys):
    keys_data = []
    for _ in keys:
        keys_data.append(_.data)
    print("keys:", keys_data)
    found_keys = []
    if keys is None or isinstance(keys, dict) or "Err" in keys or len(keys) == 0:
        return "Err"
    for key in keys_data:
        if key in cache.keys():
            found_keys.append(key)
    return Integer(len(found_keys))

def _handle_echo(data):
    try:
        if data == {}:
            return "Err"
        if data is not None:
            if isinstance(data, set):
                return f"*2\r\n$4\r\nECHO\r\n${len(data)}\r\n{data}\r\n"
            else:
                return "Err"
    except Exception as e:
        return "Err"

def resp_encoder_get(data:str):
    return f"*1\r\n${len(data)}\r\n{data}\r\n"

def _handle_ping():
    try:
        return f"*1\r\n$4\r\nPONG\r\n"
    except Exception as e:
        return e

def _handle_config(datastore):
    return f"+Testing Config :{datastore["CONFIG"]}\r\n"

def _handle_unrecognised_command(command):
    return ""

def _handle_set(datastore, persister):
    if datastore:
        for key in datastore.keys():
                if e.ladd(cache.Add(datastore)): # cache.add and e.ladd returns array of datastore
                    return f"+OK\r\n"
    else:
        return "Error"

def _handle_get(datastore):
    if datastore:
        for key in datastore.keys():
            result = e.get_value(cache.Get(datastore)) # returns array of datastore
            return resp_encoder_get(result)
    else:
        return "Key not found"
