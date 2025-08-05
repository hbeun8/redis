
import socket  # For network socket operations
import datetime  # For timestamp generation
import threading
from connection_handler import ConnectionHandler

def _client_thread(conn, addr, PORT, server):
    with conn:
        #print(f"Connection from: {conn}")
        #print(f"Connected by {addr[0]} {addr[1]} succeeded")
        print(f"[THREAD] conn.fileno() = {conn.fileno()}")
        if server.args.l == 'tcp':
            server._handle_tcp(conn, PORT)
        else:
            server._handle_udp(conn, PORT)

class Server:
    def __init__(self, args):
        self.args = args
        self.HOST = ''  # Open IP Address
        self.sock_type = socket.SOCK_STREAM if args.l == 'tcp' else socket.SOCK_DGRAM

    def start(self, ports):
        for PORT in ports:
            try:
                with socket.socket(socket.AF_INET, self.sock_type) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
                    s.bind((self.HOST, PORT))
                    print(f"Port {PORT} is open")
                    s.listen()
                    print("Server listening on port")
                    while True:
                        conn, addr = s.accept()
                        print(f"[MAIN] conn.fileno() = {conn.fileno()}")
                        t = threading.Thread(target=_client_thread, args=(conn, addr, PORT, self), daemon=True)
                        t.start()
            except ConnectionError:
                print(f"Port {PORT} is closed or in use")

    def _handle_tcp(self, conn, port):
        with conn:
            handler = ConnectionHandler(conn)
            #print("Connection established", conn)
            if self.args.e:
                handler.handle_echo_loop(self.args.e)
            elif self.args.x:
                handler.handle_hex_dump()
            elif self.args.a:
                handler.handle_ping_pong_loop()
            elif self.args.i:
                #print("Now in Interactive mode")
                handler.handle_execute()
            elif self.args.z:
                pass  # Just connect and close
            # default echo loop
            else:
                handler.handle_echo_loop()

    def shutdown(self, conn):
        conn.close()

    def _handle_udp(self, s, port):
        print(f"Hi! UDP server on port {port}")
        while True:
            data, addr = s.recvfrom(1024)
            date_str = str(datetime.datetime.now()).encode()
            s.sendto(date_str, addr)


