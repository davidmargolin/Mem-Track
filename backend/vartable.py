class VarTable:
    def __init__(self):
        self.table = []

    def addVar(self, name, type, address, varCount):
        self.table.append({"number": varCount, "name": name, "type": type, "address": address})

    def address(self, search):
        for item in self.table:
            tmp = item["name"]
            if tmp == search:
                return item["address"]
        return " ERROR: variable '" + search + "' not found "
