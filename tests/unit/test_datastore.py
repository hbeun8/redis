import pytest
from datastore import Datastore, Dict

def test_dict_base_case():
    data = {"foo": "bar", "Expiry": "25/07/25", "type": "123"}
    c = Dict(data)
    result_key = c.key
    result_value = c.value
    result_expiry = c.expiry
    result_type = c.type
    result_s = c.s
    result_u_s = c.u_s
    assert result_key == "foo"
    assert result_value == "bar"
    assert result_expiry == "25/07/25"
    assert result_type == "123"
    assert result_s == "bar:25/07/25:123"
    assert result_u_s == {"foo": "bar", "Expiry": "25/07/25", "type": "123"}

def test_dict_missing_parameters():
    data = {None: None, None: None, None: None}
    c = Dict(data)
    result_key = c.key
    result_value = c.value
    result_expiry = c.expiry
    result_type = c.type
    result_s = c.s
    result_u_s = c.u_s
    assert result_key == None
    assert result_value == None
    assert result_expiry == None
    assert result_type == None
    assert result_s == "None:None:None"
    assert result_u_s == {None: None, None: None, None: None}

def test_datastore_getter_setter():
    data = {"Name": "Varun", "Expiry": "25/07/25", "Type": 123}
    c = Datastore(data)
    set_result = c.Add("Name", "Varun:25/07/25:123")
    get_result = c.Get("Name")
    assert set_result == "+OK"
    assert get_result == "Varun:25/07/25:123"

# Not sure whats going on here
def test_datastore_add_missing_key_value():
    data = {"Name": None, "Expiry": None, "Type": None}
    c = Datastore(data)
    result = c.Add("",  "")
    assert result == "-Err"

def test_datastore_add_base_case():
    data = {"Name": "Varun", "Expiry": "25/07/25", "Type": 123}
    c = Datastore(data)
    result = c.Add("Name", "Varun:25/07/25:123")
    assert result == "+OK"

def test_datastore_add_missing_value():
    data = {"Name": "Varun", "Expiry": "25/07/25", "Type": 123}
    c = Datastore(data)
    result = c.Add("name", None)
    assert result == "-ERR wrong number of arguments for 'set' command"

def test_datastore_add_key_already_exists():
    data = {"Name": "Varun", "Expiry": "25/07/25", "Type": 123}
    c = Datastore(data)
    result = c.Add("Name", "Raval")
    assert result == "+OK"

def test_datastore_get_base_cases():
    data = {"Name": "Varun", "Expiry": "25/07/25", "Type": 123}
    c = Datastore(data)
    result = c.Add("Name", "Varun:25/07/25:123")
    result = c.Get("Name")
    assert result == "Varun:25/07/25:123"

def test_datastore_get_key_not_found():
    data = {"Invalid Key": "To be Found", "Expiry": None, "Type": None }
    c = Datastore(data)
    result = c.Get("Key")
    assert result == "(nil)"