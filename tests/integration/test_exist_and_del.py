import subprocess

def test_exists(server):
    res = subprocess.run(["redis-cli", "-p", "8001", "exists", "invalid key"], stdout=subprocess.PIPE)
    assert res.returncode == 0
    assert res.stdout