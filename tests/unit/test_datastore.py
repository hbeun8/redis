import pytest
from datastore import Datastore

def test_datastore_getter_setter():
    d = Datastore()
    result = d.Add("key", "value")
    assert d.key == "value"
    assert d.value == 0

'''
How to test when read when the lock is on

'''
