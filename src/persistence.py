'''
We have two options for persistence:
    1. snapshotting
    2. append-only file (fn) -> opens the file and logs the command to the file.

AOF persistence logs every write operation received by the server.
These operations can then be replayed again at server startup,
reconstructing the original dataset. Commands are logged using the
same format as the Redis protocol itself.

Consider fsync policy to speed it up.

'''

from protocol_handler import Parser
import threading

class AppendOnlyPersister:
    def __init__(self, filename):
        self._filename = filename
        self._file = open(filename, mode='ab', buffering=0)

    def log_command(self, command="", data):
        # Write the length of the command followed by the encoded command items
        self._file.write(f"{len(command)}\n".encode())
        for item in data:
            self._file.write(self.resp_serialized(data).encode())

    def resp_serialized(self, data: str):
        if data is None or "":
            return "OK"
        else:
            _comp = f"${len(data)}\r\n{data}\r\n"
            return _comp

    # Returns first and last consecutive keys (and maybe appends set keys) and removes everything in the middle and save in flattened.aof
    # After running this command, it runs the check the command.
    def flatten(self):
        with self._file as f:
            for buffer in f:
                frames, frame_size = parser.parse_frame(buffer)
                key, value = frames[1], frames[2]
                keys_to_be_deleted = [buffer[i + 1] for i in range(len(b) - 2) if
                                          b[i][0] == b[i + 1][0] and b[i][0] == b[i + 2][0]]
                    # print(keys_to_be_deleted)
                    for key in keys_to_be_deleted:
                        b.remove(key)
                    return b
                except Exception as e:
                    return e
        # build new_logs.
        for each command and datastroe in array:
            self.log_command(command, data)

    def checks:
        with self.file in f:
            for buffer in f:
                generate a dictionary that will groupby file into command and key to fin_value


    def log_rebuild(self, repl_filename):
        repl = open(repl_filename, mode='ab', buffering=0)
        with self._file as f:
            for line in f:
                repl.write(line)

    def safe_flatten(self):
        t = threading.Thread(target=self.flatten, args=(), daemon=True)
        t.start()

    def safe_log_rebuild(self, repl_filename):
        t = threading.Thread(target=self.safe_log_rebuild, args=(repl_filename), daemon=True)
        t.start()


def restore_from_file(filename, datastore):
    buffer = bytearray()
    parser = Parser(buffer)
    with open(filename, "rb") as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            buffer.extend(data)
    return buffer

