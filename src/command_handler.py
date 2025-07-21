
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
            return _handle_set(command, datastore, persister)
        case "GET":
            return _handle_get(command, datastore)
        case _:
            return _handle_unrecognised_command(command)


def _handle_echo(data):
    try:
        return f"+{data["ECHO"]}\r\n"
    except Exception as e:
        print("We have reached Echo Handler and return the error message ", e)


def _handle_ping():
    try:
        result = "PONG"
        return f"+{result}\r\n"
    except Exception as e:
        print(e)

def _handle_unrecognised_command(command):
    return ""