import subprocess

def test_ping(server):
    res = subprocess.run(["redis-cli", "PING"], stdout=subprocess.PIPE)
    assert res.returncode == 0
    assert res.stdout.decode("utf-8").strip() == "PONG"

    res = subprocess.run(["redis-cli","PING", "HELLO"], stdout=subprocess.PIPE)
    assert res.returncode == 0
    assert res.stdout.decode("utf-8").strip() == "Hello"