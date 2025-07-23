
from datastore import Datastore
from expiry import Expiry
cache = Datastore({"key": "value", "Expiry": "value"})
e = Expiry({"key": "value", "Expiry": "value"})
def handle_command(command, datastore, persister=None):
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
            return handle_exists(command, datastore)
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
            return _handle_get(command, datastore)
        case _:
            return _handle_unrecognised_command(command)


def _handle_echo(data):
    try:
        return f"*2\r\n$4\r\nECHO\r\n${len(data)}\r\n{data}\r\n"
    except Exception as e:
        print()


def _handle_ping():
    try:
        return f"*1\r\n$4\r\nPING\r\n"
    except Exception as e:
        print(e)

def _handle_config(datastore):
    return f"+Testing Config :{datastore["CONFIG"]}\r\n"

def _handle_unrecognised_command(command):
    return ""

def _handle_set(datastore):
    if datastore:
        for key in datastore.keys():
                e.ladd(cache.Add(datastore)) # returns array of datastore
        return f"+OK\r\n"
    else:
        return "Error"

def _handle_get(datastore, key):
    if datastore:
        return f"+{datastore[key]}\r\n"
    else:
        return "Key not found"
