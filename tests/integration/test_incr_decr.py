import subprocess

def test_exists(server):
    res = subprocess.run(["redis-cli", "-p", "8001", "set", "validkey", "10"], stdout=subprocess.PIPE)
    assert res.returncode == 0
    assert res.stdout.decode("utf-8").strip() == "OK"

    res = subprocess.run(["redis-cli", "-p", "8001", "incr", "validkey"], stdout=subprocess.PIPE)
    assert res.returncode == 0
    assert res.stdout.decode("utf-8").strip() == "(integer) 11"