
from datetime import datetime, timedelta
from dateutil.parser import parse

class Expiry:
    def __init__(self, data:dict):
        self._arr = [data if data["Expiry"] is not None else None]
        self.curr = datetime.now()

    def radd(self, data):
        data["type"] = 0 if "type" in data.keys() else None# This ensures the data is retrievable because not expired.
        self._arr.append(data)
        return data

    def ladd(self, data):
        temp_arr = []
        data["type"] = 0 if "type" in data.keys() else None  # This ensures the data is retrievable because not expired.
        if data["Expiry"]  is not None:
            temp_arr.insert(0, data)
            for _ in range(len(self._arr)):
                temp_arr.append(self._arr[_])
        self._arr = temp_arr
        return data

    def sort(self):
        def rExpiry(e):
            return e.expiry
        return self._arr.sort(reverse=True, key=rExpiry)

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

    def get_value(self, datastore):
        for _ in range(len(self._arr)):
            for key in self._arr[_].keys():
                for ds_key in datastore.keys():
                    if key == ds_key:
                        # if Expired? set type = 1
                        if self._arr[_]["Expiry"] is not None:
                            # if Expired? set type = 1
                            if isExpired(self._arr[_]["Expiry"]):
                                self._arr[_]["type"] = 1
                                return "+Expired\r\n"
                        return self._arr[_][key]

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

'''
Adatastore = {
    "Key" : "Value",
    "Expiry" : "Date",
    "Type": "Value"
}
'''