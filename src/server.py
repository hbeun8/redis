
import socket  # For network socket operations
import datetime  # For timestamp generation
import threading

from connection_handler import ConnectionHandler
from dataclasses import dataclass

class Server:
    def __init__(self, args):
        self.args = args
        self.HOST = ''  # Open IP Address
        self.sock_type = socket.SOCK_STREAM if args.l == 'tcp' else socket.SOCK_DGRAM

    def start(self, ports):
        for PORT in ports:
            try:
                with socket.socket(socket.AF_INET, self.sock_type) as s:
                    s.bind((self.HOST, PORT))
                    print(f"Port {PORT} is open")

                    if self.args.l == 'tcp':
                        self._handle_tcp(s, PORT)
                    else:
                        self._handle_udp(s, PORT)
            except ConnectionError:
                print(f"Port {PORT} is closed or in use")

    def _handle_tcp(self, s, port):
        s.listen(1)
        print(f"Server listening on port")
        conn, addr = s.accept()
        thread = threading.Thread(target=self._handle_tcp, args=(conn, port))
        thread.start()
        thread.join()
        with conn:
            print(f"Connected by {addr[0]} {addr[1]} succeeded")
            handler = ConnectionHandler(conn)
            if self.args.e:
                handler.handle_echo_loop(self.args.e)
            elif self.args.x:
                handler.handle_hex_dump()
            elif self.args.a:
                handler.handle_ping_pong_loop()
            elif self.args.i:
                handler.handle_execute()
            elif self.args.z:
                pass  # Just connect and close
            # default echo loop
            else:
                handler.handle_echo_loop()
    def close(self):
        self.close()

    def _handle_udp(self, s, port):
        print(f"Hi! UDP server on port {port}")
        while True:
            data, addr = s.recvfrom(1024)
            date_str = str(datetime.datetime.now()).encode()
            s.sendto(date_str, addr)