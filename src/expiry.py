
from datetime import datetime, timedelta

class Expiry:
    def __init__(self, data):
        self._arr = [data if data["Expiry"] is not None else None]
        self.curr = datetime.now()

    def radd(self, data):
        self._arr.append(data)
        return data

    def ladd(self, data):
        temp_arr = []
        if data.expiry is not None:
            temp_arr[0] = data
            for _ in range(len(self._arr)):
                temp_arr.append(self._arr[_])
        self._arr = temp_arr

    def sort(self):
        def rExpiry(e):
            return e.expiry
        return self._arr.sort(reverse=True, key=rExpiry)

    def set_new_expiry(self, key, expiry=0):
        for _ in range(len(self._arr)):
            if self.arr[_]["Expiry"] is not None:
                self.arr[_]["Expiry"] = self.curr + timedelta(seconds=expiry)
        return self

    def __str__(self):
        print("Datastore r sorted by expiry:")
        for _ in self._arr:
            print(_)


Adatastore = {
    "Key" : "Value",
    "Expiry" : "Date",
    "Type": "Value"
}