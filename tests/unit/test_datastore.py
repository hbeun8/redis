import pytest
from datastore import Datastore

def test_datastore_getter_setter():
    data = {"Name": "Varun", "Expiry": "25/07/25", "Type": 123}
    d = Datastore(data)
    result = d.Add(data)
    assert result["Name"] == "Varun"
    assert result["Expiry"] == "25/07/25"

'''
How to test when read when the lock is on
We need test multiple datasources
'''
