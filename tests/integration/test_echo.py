import subprocess

def test_echo(server):
    res = subprocess.run(["redis-cli", "-p", "8001", "ECHO", "HELLO"], stdout=subprocess.PIPE)
    assert res.returncode == 0
    assert res.stdout. decode ("utf-8"). strip() == "HELLO"