import time
import threading

import pytest
from main import main
from server import Server as s
@pytest.fixture
def server(scope="module"):
    threading.Thread(target=main, daemon=True).start()
    time.sleep(0.1)
    yield
    s.shutdown()