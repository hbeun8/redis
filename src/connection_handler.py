
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
            if cmd == 'COMMAND':  #
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
                    ds="-Err message\r\n"
                _echo_data = self.resp_serialized(ds)
                self.conn.send(_echo_data.encode())
                continue
            # default option
            option = "vanilla"
            datastore =  {} # proxy for now
            if cmd == 'GET':
                kwarg_key = self.isvalid(frames, 1, "None"),
                if option == "vanilla":
                    datastore = {kwarg_key[0]: "TO BE FOUND", "Expiry": "TO BE FOUND"}
            else:
                if len(frames) == 2:
                    if cmd == "SET":
                        self.conn.send(self.resp_serialized("Err").encode())
                        continue
                    datastore = {getattr(frames[1], "data"): "NONE", "Expiry": "NONE"}
                elif len(frames) > 2 :
                    kwarg_key = self.isvalid(frames, 1, "None"),
                    kwarg_value = self.isvalid(frames, 2, "None"),
                    kwarg_ex_px = self.isvalid(frames, 3, "Expiry"),
                    kwarg_ex_px_value = self.isvalid(frames, 4, "None"),
                    datastore = {kwarg_key[0]: kwarg_value[0], kwarg_ex_px[0]: kwarg_ex_px_value[0]}
                    print(datastore)
            result = command_handler.handle_command(cmd, datastore)
            print("Result: " + str(result))
            output = self.resp_serialized(result)  # Consider appending any error message here
            if output:
                print(output.encode())
                self.conn.send(output.encode())
            else:
                self.conn.send(b'\n')

    def isvalid(self, data:list, index: int, safe: str):
        try:
            return getattr(data[index], "data")
        except IndexError:
            return safe


    def resp_serialized(self, data: str):
        if data is None or "":
            return "OK"
        else:
            length = 1 # hardwired
            # build:
            #_comp = f"*{length}\r\n"
            #data_comp = ''
            _comp = f"${len(data)}\r\n{data}\r\n"
            return _comp

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