# -*-coding:utf8 -*-
import ast


class Dto(dict):
    def getAsString(self, key):
        return self.transform("str", key)

    def getAsFloat(self, key):
        return self.transform("float", key)

    def getAsInt(self, key):
        return self.transform("int", key)

    def getAsTuple(self, key):
        return self.transform("tuple", key)

    def getAsDict(self, key):
        return self.transform("dict", key)

    def getAsList(self, key):
        return self.transform("list", key)

    def transform(self, datatype, key):
        if datatype in ("dict", "tuple", "list"):
            return ast.literal_eval(str(self.get(key, None)))
        elif datatype == "str":
            return self.ternary(self.get(key, None) is None, None, str(self.get(key)).strip())
        elif datatype == "float":
            return self.ternary(self.get(key, None) is None, None, float(self.get(key)))
        elif datatype == "int":
            return self.ternary(self.get(key, None) is None, None, int(self.get(key)))
        else:
            return None

    def ternary(self, condition, ture_part, false_part):
        return (condition and [ture_part] or [false_part])[0]


if __name__ == "__main__":
    a = {"name": "zhangsan", "age": 23, "fav": "('篮球', '足球')", "fam": "{'mother':'haha', 'father':'hhhh'}", "aa": ""
                 }
    test = Dto()
    test.update(a)
    # print type(a["help"])
    # test.update(a)
    # print type(test.getAsList("fam"))
    print test.getAsDict("fam")
    # print test.getAsTuple("fav")
    # print type(test.getAsNumber("age"))
    print test.__doc__

