# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_core.ipynb (unless otherwise specified).

__all__ = ['Record', 'Lesson', 'Subject', 'Program']

# Cell
from collections import defaultdict

# Cell

class Record:

    def __init__(self, name,key = 0,sort = 0):
        self.name = name
        self.key = key
        self.sort = sort

    def adjustEmptyKey(self,others):
        if self.key < 1:
            maxVal = max([x.key for x in others])
            self.key = maxVal + 1
        if self.sort == 0:
            self.sort = max([x.sort for x in others]) + 1

    def adjustKey(self,x):
        props = x.split('|')
        if len(props) > 2:
            self.name = props[0]
            self.key = int(props[1])
            self.sort = int(props[2])

    def keyString(self):
        return self.name + "|" + str(self.key) + "|" + str(self.sort)

    def toDict(self):
        return {"key" : self.keyString() }

    def fromDict(s):
        ret = Record("")
        ret.adjustKey(s["key"])
        return ret

    def __repr__(self):
        return self.keyString()

    def printKeys(x):
        s = sorted(x, key=lambda l: l.sort)
        return [y.keyString() for y in s]

    def appendUnique(x,others):
        if x.key > 0:
            others = [y for y in others if x.key != y.key]
        others.append(x)
        x.adjustEmptyKey(others)
        return others


# Cell
class Lesson(Record):
    def __init__(self, name,  filesName, key = 0,sort = 0):
        super().__init__(name,key,sort)
        self.fileName = filesName
        self.modifyTime = float(0)
        self.indexPath = []

    def sBase(self):
        if self.modifyTime > 0:
            return  self.modifyTime
        return float(self.sort)

    def keyString(self):
        return  super().keyString() + "|" + self.fileName

    def adjustKey(self,x):
        super().adjustKey(x)
        props = x.split('|')
        if len(props) > 3:
            self.fileName = props[3]

    def appendUniqueFile(x,others):
        ret = [y for y in others if x.fileName != y.fileName]
        if len(ret) != len(others):
            return others
        return Record.appendUnique(x,others)

    def toDict(self):
        ret = super().toDict()
        ret["modifyTime"] = self.modifyTime
        ret["fileName"] = self.fileName
        ret["indexPath"] = self.indexPath
        return ret

    def fromDict(s):
        ret = Lesson("","")
        ret.adjustKey(s["key"])
        ret.modifyTime = s["modifyTime"]
        ret.fileName = s["fileName"]
        ret.indexPath = s["indexPath"]
        return ret

    def __str__(self):
        return "[" + str(self.key) + "]" + self.fileName


# Cell

class Subject(Record):
    def __init__(self, name,key = 0,sort = 0):
        super().__init__(name,key,sort)
        self.lessons = []
        self.sequences = defaultdict(list)
        self.lookup = {}
        self.img = ""

    def addLesson(self,x):
        self.lessons = Lesson.appendUniqueFile(x,self.lessons)
        self.lookup[x.key] = x

    def toDict(self):
        ret = super().toDict()
        ret["lessons"] = [x.toDict() for x in self.lessons]
        seq = {}
        for key, value in self.sequences.items():
            seq[key] = value
        ret["sequences"] = seq
        ret["img"] = self.img
        return ret

    def fromDict(d):
        ret = Subject("","")
        ret.adjustKey(d["key"])
        ret.lessons = [ Lesson.fromDict(s) for s in d["lessons"]]

        for x in ret.lessons:
            ret.lookup[x.key] = x

        for key, value in d["sequences"].items():
            ret.sequences[key] = value
        ret.img = d["img"]
        return ret

    def __repr__(self):

        return self.name + "; [" + ",".join( Record.printKeys(self.lessons)) + "]"

    def __str__(self):
        return '__str__ for Car'

# Cell
class Program(Record):
    def __init__(self, name, path = ".",key = 0,sort = 0 ):
        super().__init__(name,key,sort)
        self.subjects = []
        self.title = name
        self.lookup = {}
        self.img = ""

    def toDict(self):
        ret = super().toDict()
        ret["subjects"] = [x.toDict() for x in self.subjects]
        ret["title"] = self.title
        ret["img"] = self.img
        return ret

    def fromDict(d):
        ret = Program("")
        ret.adjustKey(d["key"])
        ret.subjects = [Subject.fromDict(s) for s in d["subjects"]]
        ret.title = d["title"]
        for x in ret.subjects:
            ret.lookup[x.key] = x
        ret.img = d["img"]
        return ret


    def fixPaths(self):
        for progIndex, sub in self.lookup.items():
            for subIndex, lesson in sub.lookup.items():
                lesson.indexPath = [progIndex,subIndex]

    def addSubject(self,x):
        self.subjects = Subject.appendUnique(x,self.subjects)
        self.lookup[x.key] = x

    def __repr__(self):
        return self.name + "Program, Subjects[" + ";".join( Record.printKeys(self.subjects)) +"]"

    def __str__(self):
        return '__str__ for Car'