# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/03_StaticGenerator.ipynb (unless otherwise specified).

__all__ = ['Render', 'makeSite']

# Cell
import os
import sys
import shutil
import json
from jinja2 import Environment, FileSystemLoader, Template

# Cell
from .School import StudySystem
from .Program import Program, Subject, Record, Lesson
from .munge import  dateGrid, processGuide, unassignedForSubject, printAllUnassigned

# Cell

class Render:
    def __init__(self, program, guide , dir="../../web",template = "../templates"):

        self.guide = guide
        self.program = [x for x in guide.programs if x.name == program][0]
        print("loaded program " + self.program.name)
        self.outputdir = os.path.join(dir,self.program.name)
        self.template = template

        self.file_loader = FileSystemLoader(self.template)
        self.env = Environment(loader=self.file_loader)
        self.resourcesName =  "resources"
        self.resourcesStart = os.path.join(".", self.resourcesName )
        self.resourcesEnd =  os.path.join(self.outputdir,self.resourcesName)



    def basePath(self):
        return self.outputdir

    def renderLesson(self,sub,lesson):
        template = self.env.get_template("lesson.html")
        resDir = "../../.."

        output = template.render(item=sub,
                                 resDir=resDir,
                                 less=lesson,
                                 program = self.program,
                                 styleDir=os.path.join("..",self.resourcesName))
        subDir = os.path.join(self.outputdir,sub.name)

        if not os.path.exists(subDir):
            os.mkdir(subDir)
        f = open(os.path.join(subDir,"vid_" +str(lesson.key) + ".html"), "w")
        f.write(output)

    def renderSubject(self,sub):
        template = self.env.get_template("subject.html")
        videos = [x for x in sub.lessons if x.fileName.endswith(".mp4")]
        resources = [x for x in sub.lessons if not x.fileName.endswith(".mp4")]
        for x in sub.lessons:
            self.renderLesson(sub,x)
        resDir = "../../.."
        #print(sub.sequences)
        output = template.render(item=sub,
                                 videos=videos,
                                 res=resources,
                                 resDir=resDir,
                                 program = self.program,
                                 grid = reversed(dateGrid(self.program,subject=sub.name)),
                                 styleDir=os.path.join("..",self.resourcesName))
        subDir = os.path.join(self.outputdir,sub.name)

        if not os.path.exists(subDir):
            os.mkdir(subDir)
        f = open(os.path.join(subDir,"index.html"), "w")
        f.write(output)

    def renderCalendar(self):

        grid = reversed(dateGrid(self.program))

        if not os.path.exists(self.outputdir):
            os.mkdir(self.outputdir)

        template = self.env.get_template("calendar.html")
        output = template.render(program=self.program,
                                 grid=grid,
                                 styleDir=os.path.join(".",self.resourcesName))

        f = open(os.path.join(self.outputdir,"calendar.html"), "w")
        f.write(output)
        f.close()

    def renderSchool(self):

        foo = self.program.subjects
        seq = sorted(foo, key=lambda x: x.name)

        if not os.path.exists(self.outputdir):
            os.mkdir(self.outputdir)

        for x in seq:
            self.renderSubject(x)

        template = self.env.get_template("school.html")
        output = template.render(program=self.program,
                                 seq=seq,
                                 styleDir=os.path.join(".",self.resourcesName))

        f = open(os.path.join(self.outputdir,"index.html"), "w")
        f.write(output)
        f.close()

        self.addResources()

    def addResources(self):
        if not os.path.exists(self.resourcesEnd):
            os.mkdir(self.resourcesEnd)

        src_files = os.listdir(self.resourcesStart)

        for file_name in src_files:
            full_file_name = os.path.join(self.resourcesStart, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, os.path.join(self.resourcesEnd, file_name))

        with open(os.path.join( self.resourcesEnd, "lemonade.json"), "w") as dataFile:
            json.dump(self.program.toDict(), dataFile, indent=4, sort_keys=True)

    def addFiles(self):
        for sub in self.program.subjects:
            for lesson in sub.lessons:
                source = os.path.join(self.guide.origin, self.program.name,sub.name,lesson.fileName)
                dest = os.path.join(self.outputdir,sub.name,lesson.fileName)

                if not os.path.isfile(dest):
                    print("found " + dest)
                    shutil.copy(source, dest)



# Cell
def makeSite(school,programName):
    baseRender = Render(programName,school)
    baseRender.renderSchool()
    school.save()
    baseRender.addFiles()
    baseRender.addResources()
    baseRender.renderCalendar()