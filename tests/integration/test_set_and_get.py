import subprocess

def test_set(server):
    res = subprocess.run(["redis-cli", "-p", "8001", "set", "key", "value"], stdout=subprocess.PIPE)
    assert res.returncode == 0
    assert res.stdout. decode ("utf-8"). strip() == "OK"

def test_get(server):
    res = subprocess.run(["redis-cli", "-p", "8001", "get", "key"], stdout=subprocess.PIPE)
    assert res.returncode == 0
    assert res.stdout. decode ("utf-8"). strip() == "value"