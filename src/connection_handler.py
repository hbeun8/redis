
from protocol_handler import Parser, Bulkstring, Array, Error, Integer, Simplestring
import command_handler
from persistence import restore_from_file, AppendOnlyPersister
import time
from dataclasses import dataclass
from datastore import Datastore
from command_handler import resp_encoder_get

persister = AppendOnlyPersister("log.aof")

class ConnectionHandler:
    def __init__(self, conn):
        self.conn = conn

    def handle_execute(self):
        while True:
                data = self.conn.recv(4096)
                #persister.log_command("", data)
                if not data:  # <-- peer hung up
                    break
                parser = Parser(data)
                frames, _ = parser.parse_frame(data)
                cmd = frames[0].data.upper()
                if cmd == 'COMMAND':  # Remove this if you want Persister switched on startup or you could keep it on permamnently
                    self.conn.send(b"+OK'\r\n")
                    continue  # stay connected
                if cmd == "CONFIG":
                    self.handle_config()
                    continue
                if cmd == 'PING':
                    self.conn.send(b"+PONG\r\n")
                    continue
                if cmd == "RESTORE": # or cmd == "COMMAND":
                    try:
                        buffer = restore_from_file("log.aof")
                        while True:
                            frames, frame_size = parser.parse_frame(buffer)
                            cmd = frames[0].data.upper()
                            datastore = [el.data for el in frames[1:]]
                            result = command_handler.handle_command(cmd, datastore)
                            output = self.resp_serialized(str(result))  # Consider appending any error message her
                            if output:
                                self.conn.send(output.encode())
                            else:
                                self.conn.send(b'\n')
                    except Exception as e:
                        return f"-Err (persister): {e}"

                if cmd == "BGREWRITEAOF":
                    try:
                        persister.safe_log_rebuild("replica_log.aof")
                        persister.sefe_flatten()
                        persister.check(f"{time.time_ns}.aof")
                    except Exception as e:
                        return f"-Err (BGREWRITEAOF already in progress): {e}"

                if cmd == 'ECHO':
                    if len(frames) == 2:
                        ds = frames[1].data
                        _echo_data = self.resp_serialized(ds)
                        self.conn.send(_echo_data.encode())
                        continue
                    elif len(frames) > 2:
                        ds=b'-Err\r\n'
                        self.conn.send(ds)
                        continue
                    else:
                        ds=b'-Err\r\n'
                        self.conn.send(ds)
                        continue

                datastore = [el.data for el in frames[1:]]
                result = command_handler.handle_command(cmd, datastore, persister)
                output = self.resp_serialized(str(result))
                if output:
                    #persister.log_command(cmd, output.encode())
                    self.conn.send(output.encode())
                else:
                    self.conn.send(b'\n')

    def resp_serialized(self, data: str):
        try:
            if data is None or "" or isinstance(data, int):
                return f"+OK\r\n"
            else:
                length = 1 # hardwired
                _comp = f"${len(data)}\r\n{data}\r\n"
                return _comp
        except Exception as e:
            return f"-{e}"

    def handle_hex_dump(self):
        data = self.conn.recv(1024)
        self.hex_dump(data)

    def handle_echo_loop(self):
        while True:
            data = self.conn.recv(1024)
            if not data: break
            self.conn.sendall(data)

    def handle_ping_pong_loop(self):
        while True:
            data = self.conn.recv(1024)
            if data == b"PING":
                self.conn.sendall(b"PONG")
            # echo:
            if data == b"PONG":
                self.conn.sendall(b"PING")

    # Hex Dump:
    # For example:
    # @ Input: Hello, World!
    # @ Returns: 00000000  48 65 6c 6c 6f 2c 20 57 6f 72 6c 64 21  Hello, World!
    # @ Output format: [offset]  [hex values]  [ASCII representation]
    def hex_dump(self, data: bytes, width: int = 16):
        for i in range(0, len(data), width):
            chunk = data[i:i + width]
            hex_chunk = ' '.join(f"{b:02x}" for b in chunk)
            ascii_chunk = ''.join((chr(b) if 32 <= b < 127 else '.') for b in chunk)
            #print(f"{i:08x}  {hex_chunk:<{width * 3}}  {ascii_chunk}")

    def handle_config(self):
        arr = ["List of supported commands:",
            "COMMAND ",
           "CONFIG",
            "DECR ",
            "DEL",
            "ECHO",
            "EXISTS",
            "INCR",
            "LPUSH",
            "LRANGE",
            "PING",
            "RPUSH",
            ]
        for el in arr:
            self.conn.send(self.resp_serialized(el).encode())