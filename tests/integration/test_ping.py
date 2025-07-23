import subprocess

def test_ping(server):
    res = subprocess.run(["redis-cli", "PING"], stdout=subprocess.PIPE)
    assert res.returncode == 0
    assert res.stdout.decode("utf-8").strip() == "PONG"

    res = subprocess.run(["redis-cli","PING", "HELLO"], stdout=subprocess.PIPE)
    assert res.returncode == 0
    assert res.stdout.decode("utf-8").strip() == "HELLO"


    '''
    Command:	set key val
    RESP: 		"*3\r\n$3\r\nset\r\n$3\r\nkey\r\n$3\r\nval\r\n"
    Command: 	get key
    RESP:		"*2\r\n$3\r\nGET\r\n$3\r\nkey\r\n"
    '''