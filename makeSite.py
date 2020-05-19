import os
import sys
import shutil
import json

from refreshment.School import StudySystem
from refreshment.Program import Program, Subject, Record, Lesson
from refreshment.munge import  printAllUnassigned, processGuide
from refreshment.Web import Render

print("Getting Started")

guide = StudySystem(filename="./nbs/data/programs.json", origin="../")
guide.schoolDepth = 3
guide.loadDirectory()

processGuide(guide)

for x in guide.programs:
    print(x.name)
    for y in x.subjects:
        print("\"" + x.name + "\",\"" + y.name + "\"")
        
cath = guide.programs[0]
printAllUnassigned(prog=cath)

#  def __init__(self, program, guide , dir="../../web",template = "../templates"):
baseRender = Render(program=cath.name,guide=guide, dir="../web",template = "./templates")
baseRender.resources = "nbs/resources"
baseRender.resourcesStart = os.path.join(".","nbs",baseRender.resourcesName)
print( baseRender.resourcesStart, baseRender.resourcesEnd  )
baseRender.renderSchool()
baseRender.addFiles()
baseRender.renderCalendar()

guide.save()

print("all done")

