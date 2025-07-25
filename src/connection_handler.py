
from protocol_handler import parse_frame, Bulkstring, Array, Error, Integer, Simplestring
import command_handler
class ConnectionHandler:
    def __init__(self, conn):
        self.conn = conn

    def handle_execute(self):
        while True:
            data = self.conn.recv(4096)
            if not data:  # <-- peer hung up
                break
            frames, _ = parse_frame(data)
            cmd = frames[0].data.upper()
            print("Command: " + cmd)
            ds = self.buildDict(frames[1:])
            # --- minimal compliance for  ---
            if cmd == 'COMMAND':  # e.g. COMMAND DOCS
                self.conn.send(b"+OK'\r\n")
                continue  # stay connected
            if cmd == 'PING':
                self.conn.send(b"+PONG\r\n")
                continue

            if cmd == 'ECHO':
                if len(frames) == 2:
                    ds = frames[1].data
                elif len(frames) > 2:
                    ds="-Err message\r\n"
                    self.conn.send(ds.encode())
                    continue
                else:
                    ds = "ECHO"
                _echo_data = self.resp_serialized(ds)
                self.conn.send(_echo_data.encode())
                continue

            if cmd == 'GET':
                datastore = {getattr(frames[1], "data"): "NONE", "Expiry": "NONE"}
            else:
                if len(frames) == 2:
                    if cmd == "SET":
                        self.conn.send(self.resp_serialized("Err").encode())
                        continue
                    datastore = {getattr(frames[1], "data"): "NONE", "Expiry": "NONE"}
                elif len(frames) == 3:
                    datastore = {getattr(frames[1], "data"): getattr(frames[2], "data"), "Expiry": "NONE"}

            result = command_handler.handle_command(cmd, datastore)
            print("Result: " + result)
            output = self.resp_serialized(result)  # Consider appending any error message here
            print("Serial Result")
            if output:
                self.conn.send(output.encode())
            else:
                self.conn.send(b'\n')

    def buildDict(self, data:list):
        if data is None:
            return {
                data[1]: data[2] if len(data) > 1 else None,
                "Expiry": None,
                "Type": None,
            }
    def buildDictforEcho(self, data:list):
        if len(data) == 0 or data is "":
            "ECHO"
        if len(data) == 1:
            temp = (data[0])
            ds = getattr(data[0], "data")
            return ds
        else:
            return self.conn.send("-Err".encode())

    def resp_serialized(self, data: str):
        if data is None or "":
            return "OK"
        else:
            length = 1 # hardwired
            # build:
            length_comp = f"*{length}\r\n"
            data_comp = ''
            data_comp += f"${len(data)}\r\n{data}\r\n"
            return length_comp+data_comp

    def handle_hex_dump(self):
        data = self.conn.recv(1024)
        self.hex_dump(data)

    def handle_echo(self):
        data = self.conn.recv(1024)
        if data:
            return self.conn.sendall(data)

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
            print(f"{i:08x}  {hex_chunk:<{width * 3}}  {ascii_chunk}")