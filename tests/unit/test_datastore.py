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

def test_datastore_incr_key_missing():
    data = {"Name": "Varun", "Expiry": "25/07/25", "Type": 123}
    c = Datastore(data)
    result = c.incr(None)
    assert result == "-ERR wrong number of arguments for 'incr' command"

def test_datastore_incr_key_not_found():
    data = {"Name": "Varun", "Expiry": "25/07/25", "Type": 123}
    c = Datastore(data)
    result = c.incr("NoName")
    assert result == "-Error: key not found"



def test_datastore_decr_key_missing():
    data = {"Name": "Varun", "Expiry": "25/07/25", "Type": 123}
    c = Datastore(data)
    result = c.incr(None)
    assert result == "-ERR wrong number of arguments for 'incr' command"

def test_datastore_decr_key_not_found():
    data = {"Name": "Varun", "Expiry": "25/07/25", "Type": 123}
    c = Datastore(data)
    result = c.decr("NoName")
    assert result == "-Error: key not found"

def test_datastore_remove_key_not_found():
    data = {"Name": "Varun", "Expiry": "25/07/25", "Type": 123}
    c = Datastore(data)
    result = c.Remove("NoName")
    assert result == "" # a key is ignored if not found.

# We currently support only single key removal.
def test_datastore_remove_base_case():
    data = {"Name": "Varun", "Expiry": "25/07/25", "Type": 123}
    c = Datastore(data)
    c.Add("Name", "Varun:25/07/25:123")
    result = c.Remove("Name")
    assert result == "(integer) 1"

def test_datastore_exists_base_case_1():
    data = {"Name": "Varun", "Expiry": "25/07/25", "Type": 123}
    c = Datastore(data)
    c.Add("Name", "Varun:25/07/25:123")
    result = c.Exists("Name")
    assert result == "(integer) 1"

def test_datastore_exists_base_case_0():
    data = {"Name": "Varun", "Expiry": "25/07/25", "Type": 123}
    c = Datastore(data)
    c.Add("Name", "Varun:25/07/25:123")
    result = c.Exists("NoName")
    assert result == "(integer) 0"


def test_datastore_exists_missing_key():
    data = {"Name": "Varun", "Expiry": "25/07/25", "Type": 123}
    c = Datastore(data)
    c.Add("Name", "Varun:25/07/25:123")
    result = c.Exists("")
    assert result == "(integer) 0"

def test_datastore_set_w_expiry_base_case_0():
    data = {"Name": "Varun", "Expiry": "25/07/25", "Type": 123}
    c = Datastore(data)
    c.Add("Name", "Varun:25/07/25:123")
    result = c.Get_w_Expiry("Name")
    assert result == "(nil)"

def test_datastore_set_w_expiry_base_case_1():
    data = {"Name": "Varun", "Expiry": "25/07/26", "Type": 123}
    c = Datastore(data)
    c.Add("Name", "Varun:25/07/26:123")
    result = c.Get_w_Expiry("Name")
    assert result == "+OK"

def test_datastore_set_w_expiry_missing():
    data = {"Name": "Varun", "Expiry": "25/07/26", "Type": 123}
    c = Datastore(data)
    c.Add("Name", "Varun:None:123")
    result = c.Get_w_Expiry("Name")
    assert result == "+OK"

def test_datastore_set_w_expiry_gibberish():
    data = {"Name": "Varun", "Expiry": "25/07/26", "Type": 123}
    c = Datastore(data)
    c.Add("Name", "Varun:Apple:123")
    result = c.Get_w_Expiry("Name")
    assert result == "+OK"

def test_datastore_set_w_expiry_gibberish_fail():
    data = {"Name": "Varun", "Expiry": "25/07/26", "Type": 123}
    c = Datastore(data)
    c.Add("Name", "Varun:Apple:123")
    result = c.Get_w_Expiry("NoName")
    assert result == "(nil)"

def test_datastore_set_new_expiry_seconds():
    data = {"Name": "Varun", "Expiry": "25/07/26", "Type": 123}
    c = Datastore(data)
    c.Add("Name", "Varun:25/07/26:123")
    result = c.set_new_expiry_px_ex("Name", 60)
    value = c.Get("Name")
    assert result == "+OK"
    assert value == 60