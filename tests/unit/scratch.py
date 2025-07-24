def handle_execute(self):
    print("INSIDE CONNECTION HANDLER", self)
    with self.conn:
        while True:
            try:
                data = self.conn.recv(1024)
                print("Received data inside connection handler line 11", data.decode('utf-8'))
                if not data: break
                # Ensure connection remains remains open
                frameArr, size = r.parse_frame(data)
                command = frameArr[0]
                print("Received from framer inside connection handler line 18", command)
                if command == 'COMMAND':
                    secure = b'*2\r\n$7\r\nCOMMAND\r\n$4\r\nDOCS\r\n'
                    self.conn.send(secure)
                if command == "PING":
                    if len(frameArr) > 1:
                        secure = ""
                        for i in range(1, len(frameArr)):
                            secure += frameArr[i] + " "
                        self.conn.send(self.resp_serialized(secure).encode())
                    else:
                        secure = self.resp_serialized("PONG")
                        self.conn.send(secure.encode())
                if command == "ECHO":
                    if len(frameArr) > 1:
                        secure = ""
                        for i in range(1, len(frameArr)):
                            secure += frameArr[i] + " "
                        self.conn.send(self.resp_serialized(secure).encode())
                    else:
                        secure = self.resp_serialized("ECHO")
                        self.conn.send(secure.encode())

                dict = {}
                if len(frameArr) > 1:
                    dict[frameArr[0].data] = frameArr[1].data
                else:
                    dict[frameArr[0].data] = ""
                result = cmd.handle_command(command.data, dict)
                print("Received result inside connection handler line 23", result)
                output = self.resp_serialized(result)  # Consider appending any error message here
                if output:
                    self.conn.send(output.encode())
                else:
                    self.conn.send(b'\n')
            except ConnectionError as e:
                print(e)