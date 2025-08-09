import subprocess

def test_list(server):
    res = subprocess.run(["redis-cli",  "-p", "8001", "LPUSH", "K", "1", "2", "3"], stdout=subprocess.PIPE)
    assert res.returncode == 0
    assert res.stdout. decode ("utf-8"). strip() == "(integer) 3"

    res = subprocess.run(["redis-cli" ,  "-p", "8001", "RPUSH", "K", "4", "5"], stdout=subprocess.PIPE)
    assert res.returncode == 0
    assert res.stdout. decode ("utf-8"). strip() == "(integer) 5"

    res = subprocess.run(["redis-cli", "-p", "8001", "LRANGE", "K", "0", "4"], stdout=subprocess.PIPE)
    assert res.returncode == 0
    assert res.stdout.decode("utf-8").strip() == "['3', '2', '1', '4']"