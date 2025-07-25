'''
We have to options for persistance:
    1. snapshotting
    2. append-only file.
'''

class AppendontyPersister: 3 usages
def
_init__(self, filename):
self._fiLename = filename
self._file = open(filename,
1ode= aD, DuTterng=0
def log_command(self, command): 8 usages (8 dynamic) & John Crickett self._file write (f"*fLen(command) Hr\n". encode())
for item in command:
selt._file.wr1te(1tem.tlle_encodeo)
def restore_from_file(filename, datastore): 2 usages 1 John Crickett
buffer = bytearray)
with open(filename, "rb") as f:
while True:
data = f.read(4096)
if not data: break
buffer.extend (data)
while True:
frame, frame_size = extract_frame_from_buffer(buffer)
if frame:
buffer = buffer[frame_size:]
result = handLe_command (frame, datastore)
if isinstance (result, Error):
print("Error corrupt AOF file")
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

