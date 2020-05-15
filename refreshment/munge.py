# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/02_DataMunge.ipynb (unless otherwise specified).

__all__ = ['removeAuthor', 'cleanName', 'cleanLesson', 'subjectWithName', 'assignLessonsWithName',
           'makePriorsForSubject', 'unassignedForSubject', 'assignCategoriesToSubject', 'loadMetaFile', 'processGuide',
           'initials', 'keyFromDate', 'dataFromDate', 'dateGrid']

# Cell
import os
import sys
import pandas as pd
import re
from time import gmtime, strftime, ctime
from datetime import datetime, timedelta
import json
from collections import defaultdict

# Cell
from .School import StudySystem,subjectFromPath
from .Program import Program, Subject, Record, Lesson

# Cell
def removeAuthor(cl):
    cl.programs = [x for x in cl.programs if x.name in ["Cathedral"]]
    for x in cl.programs:
        x.subjects = [y for y in x.subjects if y.name != "Conners"]
        x.fixPaths()

# Cell
def cleanName(x,removeExtension=True):
    label = re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', x)
    if removeExtension and label[-4] == ".":
        label = label[:-4]
    label = re.sub(' +', ' ', label)

    return label

def cleanLesson(less):
    for l in less.lessons:

        label = cleanName(l.fileName)
        if l.name == l.fileName:
            l.name = label



# Cell
def subjectWithName(prog,name):
    return [x for x in prog.subjects if x.name ==name][0]

def assignLessonsWithName(sub,express):
    howTo = [x for x in sub.lessons if express in x.name]
    howTo.sort(key=Lesson.sBase)
    return [x.key for x in howTo]


# Cell
def makePriorsForSubject(sub):
    skips = {}
    for (key, seq) in sub.sequences.items():
        i = 0
        for x in seq:
            less = sub.lookup[x]
            less.prior = seq[:i]
            less.next = seq[i+1:]
            i += 1
            skips[x] = 1

    unassigned = [x.key for x in sub.lessons if not x.key in skips]
    i = 0
    for x in unassigned:
        less = sub.lookup[x]
        less.prior = unassigned[:i]
        less.next = unassigned[i+1:]
        i += 1



# Cell
def unassignedForSubject(sub):
    skips = {}
    for (key, seq) in sub.sequences.items():
        i = 0
        for x in seq:
            skips[x] = 1

    return [x for x in sub.lessons if not x.key in skips]


# Cell
def assignCategoriesToSubject(sub,cats):
    nameLookUp = {}
    for x in sub.lessons:
        nameLookUp[x.fileName] = x.key
    for (k,v) in cats.items():
        sub.sequences[k] = [ nameLookUp[x] for x in v]


# Cell
def loadMetaFile(guide,program,subject,filename="meta.json"):
    ret = {}
    metaPath = os.path.join(guide.origin,program.name,subject.name,filename)
    if os.path.exists(metaPath):
        with open(metaPath) as json_file:

            trans = json.load(json_file)
            expressions = trans["expressions"]
            for (k,v) in expressions.items():
                subject.sequences[k] = assignLessonsWithName(subject,v)
            assignCategoriesToSubject(subject,trans["assignments"])
            ret = trans
    return ret


# Cell
def processGuide(gu):
    removeAuthor(gu)
    for prog in gu.programs:
        prog.title = cleanName(prog.name,removeExtension=False)
        for sub in prog.subjects:
            sub.title =  cleanName(sub.name,removeExtension=False)
            cleanLesson(sub)
            loadMetaFile(gu,prog,sub)
            makePriorsForSubject(sub)

    cath = [x for x in gu.programs if x.name == "Cathedral"][0]
    cath.title = "K"
    cath.img = "CathedralSchool_Logo_Horizontal_White.png"



# Cell
def initials(x):
    ret = []
    i = 0
    addLower = False
    for c in x:
        i = i + 1
        if c.isupper():
            ret.append(c)
            if i < len(x) and x[i].islower():
                ret.append(x[i])
                if i + 1 < len(x) and x[i+1].islower():
                    ret.append(x[i+1])
    return  "".join(ret)

# Cell
def keyFromDate(d):
    return str(d.year) + "." + str(100 + d.month) + "." + str(100 +d.day)


def dataFromDate(aDate,less,res):
    key = keyFromDate(aDate)
    return {"date":aDate.strftime("%B %d, %Y"),"lessons":less[key],"resources":res[key] }


def dateGrid(prog,subject=""):
    allLessons = defaultdict(lambda: defaultdict(list))
    resources = defaultdict(lambda: defaultdict(list))


    startDate = datetime(year=3000,month=1,day=1)
    endDate = datetime(year=1900,month=1,day=1)
    for y in prog.subjects:
        if subject == "" or subject == y.name:
            for z in y.lessons:
                dt_object = datetime.fromtimestamp(z.modifyTime)
                if dt_object < startDate:
                    startDate = dt_object
                if dt_object > endDate:
                        endDate = dt_object
                key = keyFromDate(dt_object)
                if z.fileName.endswith(".mp4"):
                    allLessons[key][y.name].append(z)
                else:
                    resources[key][y.name].append(z)


    days = list(allLessons.keys())
    days.sort()


    currentDate = startDate
    weeks=[]
    currentWeek = []
    delta = timedelta(days=1)


    while keyFromDate(endDate) != keyFromDate(currentDate):
        currentWeek.append(dataFromDate(currentDate,allLessons,res=resources))
        if currentDate.strftime("%w")=="0":
            weeks.append(currentWeek)
            currentWeek = []
        currentDate += delta


    currentWeek.append(dataFromDate(endDate,allLessons,res=resources))
    weeks.append(currentWeek)

    return weeks



