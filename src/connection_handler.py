
import subprocess  # For executing system commands
import shlex  # For shell-like syntax parsing

import protocol_handler as r
import command_handler as cmd
class ConnectionHandler:
    def __init__(self, conn):
        self.conn = conn

    def handle_execute(self):
        while True:
            data = self.conn.recv(1024)
            print(self.conn)
            print(data)
            if not data: break
            frameArr, size = r.parse_frame(data)
            print(frameArr)
            command = frameArr[0]
            datastore = {}
            if len(frameArr) > 1:
                datastore[frameArr[0].data] = frameArr[1].data
            else:
                datastore[frameArr[0].data] = ""
            print("Datastore: ", datastore)
            print("Command: ", command.data)
            result = cmd.handle_command(command.data, datastore)
            output = result # Consider appending any error message here
            print("Encoded Output", output.encode())
            if output:
                self.conn.send(output.encode())
            else:
                self.conn.send(b'\n')

    def handle_hex_dump(self):
        data = self.conn.recv(1024)
        self.hex_dump(data)

    def handle_echo(self):
        data = self.conn.recv(1024)
        if data:
            print(f"Received and Sent: {data.decode()}")
            return self.conn.sendall(data)

    def handle_echo_loop(self):
        while True:
            data = self.conn.recv(1024)
            if not data: break
            print(f"Received and Sent: {data.decode()}")
            self.conn.sendall(data)

    def handle_ping_pong_loop(self):
        while True:
            data = self.conn.recv(1024)
            if data == b"PING":
                print(f"Received and Sent: {data.decode()}")
                self.conn.sendall(b"PONG")
            # echo:
            if data == b"PONG":
                print(f"Received and Sent: {data.decode()}")
                self.conn.sendall(b"PING")

    # Hex Dump:
    # For example:
    # @ Input: Hello, World!
    # @ Returns: 00000000  48 65 6c 6c 6f 2c 20 57 6f 72 6c 64 21  Hello, World!
    # @ Output format: [offset]  [hex values]  [ASCII representation]
    def hex_dump(self, data: bytes, width: int = 16):
        print(f"Received {len(data)} bytes from the socket")
        for i in range(0, len(data), width):
            chunk = data[i:i + width]
            hex_chunk = ' '.join(f"{b:02x}" for b in chunk)
            ascii_chunk = ''.join((chr(b) if 32 <= b < 127 else '.') for b in chunk)
            print(f"{i:08x}  {hex_chunk:<{width * 3}}  {ascii_chunk}")