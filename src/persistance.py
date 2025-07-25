'''
We have to options for persistance:
    1. snapshotting
    2. append-only file.
'''

class AppendOnlyPersister:
    def __init__(self, filename):
        self._filename = filename
        self._file = open(filename, mode='ab', buffering=0)

    def log_command(self, command):
        # Write the length of the command followed by the encoded command items
        self._file.write(f"{len(command)}\n".encode())
        for item in command:
            self._file.write(item.encode())

def restore_from_file(filename, datastore):
    buffer = bytearray()
    with open(filename, "rb") as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            buffer.extend(data)

    while True:
        frame, frame_size = extract_frame_from_buffer(buffer)
        if not frame:
            break
        buffer = buffer[frame_size:]
        result = handle_command(frame, datastore)
        if isinstance(result, Error):
            print("Error: corrupt AOF file")
            return



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

