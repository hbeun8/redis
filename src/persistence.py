'''
We have two options for persistence:
    1. snapshotting
    2. append-only file (fn) -> opens the file and logs the command to the file..

AOF persistence logs every write operation received by the server.
These operations can then be replayed again at server startup,
reconstructing the original dataset. Commands are logged using the
same format as the Redis protocol itself.

Consider fsync policy to speed it up.

'''

from protocol_handler import parse_frame
from command_handler import handle_command
import threading

class AppendOnlyPersister:
    def __init__(self, filename):
        self._filename = filename
        self._file = open(filename, mode='ab', buffering=0)

    def log_command(self, command, data):
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

    # Find first and last consecutive commands and replace items and delete those items
    def shortest_path(self):
        with self._file as f:
            for buffer in f:
                #for command_and_datastore in framed(buffer):
                    #append_to_array_{command_datastore}
                    #this appends to the array -> returns_last command_and_datastore_identify_grouped_commands(command, datastore)# this is a buffer
                    #for each ele in data
                        store sdata in a temp array
                            if the next data is same as above, store in temp array
                                else ignore
                        return first and last elements of array [0. -1]
        # build new_logs.
        for each command and datastroe in array:
            self.log_command(command, data)

    def checks:
        with self.file in f:
            for buffer in f:
                generate a dictionary that will groupby file into command and key to fin_value

    def safe_log_rewrite_atomic_build(self, repl_filename):
        # log rewriting:
        # log rewriting is completely safe:
        repl = open(repl_filename, mode='ab', buffering=0)
        with self._file as f:
            for line in f:
                repl.write(line)

    def rebuild_aof(self, repl_filename):
        thread = threading.Thread(target=self.safe_log_rewrite_atomic_build, args=(repl_filename), daemon=True)
        thread.start()


def restore_from_file(filename, datastore):
    buffer = bytearray()
    with open(filename, "rb") as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            buffer.extend(data)

    while True:
        frames, frame_size = parse_frame(buffer)
        if not frames:
            break
        cmd = frames[0].data.upper()
        kwarg_key = isvalid(frames, 1, "None"),
        kwarg_value = isvalid(frames, 2, "None"),
        kwarg_ex_px = isvalid(frames, 3, "Expiry"),
        kwarg_ex_px_value = isvalid(frames, 4, "None"),
        datastore = {kwarg_key[0]: kwarg_value[0], kwarg_ex_px[0]: kwarg_ex_px_value[0]}
        result = handle_command(cmd, datastore)
        if isinstance(result, Exception):
            print("Error: corrupt AOF file")
            return

def isvalid(self, data:list, index: int, safe: str):
    try:
        return getattr(data[index], "data")
    except IndexError:
        return safe

def stop_expiry_monitor():
# it will include datastore.ticker.Stop()
# While True:
# it will remove expired keys from the store
# it will sleep 1 min.

'''
Data Store is a class
If there is no Datastore use aof.
'''

'''
def create_task()????????
'''

'''
loop over create server
'''

