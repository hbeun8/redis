import time
import threading

import pytest
from main import main
from server import Server

@pytest.fixture
def server(scope="module"):
    server_thread = (threading.Thread(target=main, daemon=True))
    server_thread.start()
    time.sleep(0.1)
    yield
    #server_thread.shutdown()