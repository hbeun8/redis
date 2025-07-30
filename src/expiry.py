
from datetime import datetime, timedelta
from timeit import Timer
from random import randint
from dateutil.parser import parse

class Expiry:
    def __init__(self, data:dict):
        self._data = {}
        self.curr = datetime.now()
        self.key = next(iter(data))

    def radd(self, data):
        if hasattr(data, "Expiry"):
            if getattr(data, "Expiry") is not None or not "":
                setattr(self._data, self.key, data)
            return data

    def ladd(self, data):
        if hasattr(data, "Expiry"):
            if getattr(data, "Expiry") is not None or not "":
                setattr(self._data, self.key, data)
            return data

    def set_new_expiry(self, key, expiry=0):
        for _ in range(len(self._arr)):
            if self.arr[_]["Expiry"] is not None:
                self.arr[_]["Expiry"] = self.curr + timedelta(seconds=expiry)
        return self

    def get_ds(self, datastore):
        for _ in range(len(self._arr)):
            for key in self._arr[_].keys():
                for ds_key in datastore.keys():
                    if key == ds_key:
                        if self._arr[_]["Expiry"] is not None:
                            # if Expired? set type = 1
                            if isExpired(self._arr[_]["Expiry"]):
                                self._arr[_]["type"] = 1
                                return "+Expired\r\n"
                        return self._arr[_]


    def get_value(self, v):
        return v

    '''
    def passive_scan(self, delay, quantity):
        idx = self._build_index(quantity) # randomly build index
        for id in idx:
            wait(delay)
            self._key_set_type(key)

    def key_set_type(self, key):
        #param key:
        #:return: datastore
        #:sideeffect: toggle type = 1 if expired or 0 otherwise
        key_ex = self._get_expiry(key)
        if key_ex is not None:
            if check if the expiry is less or more than cuttoff
                set type = 1
                else
                set type = 0
    '''

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def keys(self):
        return self._data.keys()

    def __str__(self):
        print("Datastore r sorted by expiry:")
        for _ in self._arr:
            print(_)


def isExpired(expiry):
    if expiry is None:
        return False
    return datetime.now() > parse(expiry)


