# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/05_staticGenerator.ipynb (unless otherwise specified).

__all__ = ['Render']

# Cell
import os
import sys
import shutil
from jinja2 import Environment, FileSystemLoader, Template

# Cell
from .School import StudySystem
from .Program import Program, Subject, Record, Lesson
from .munge import makePriorsForSubject

# Cell

class Render:
    def __init__(self, program, dir="../../web",template = "../templates"):
        self.program = program
        self.outputdir = os.path.join(dir,program.name)
        self.template = template

        self.file_loader = FileSystemLoader(self.template)
        self.env = Environment(loader=self.file_loader)
        self.resources = "resources"


    def basePath(self):
        return self.outputdir

    def renderLesson(self,sub,lesson):
        makePriorsForSubject(sub)
        template = self.env.get_template("lesson.html")
        resDir = "../../.."

        output = template.render(item=sub,
                                 resDir=resDir,
                                 less=lesson,
                                 program = self.program,
                                 styleDir=os.path.join("..",self.resources))
        subDir = os.path.join(self.outputdir,sub.name)

        if not os.path.exists(subDir):
            os.mkdir(subDir)
        f = open(os.path.join(subDir,"vid_" +str(lesson.key) + ".html"), "w")
        f.write(output)

    def renderSubject(self,sub):
        makePriorsForSubject(sub)
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
                                 styleDir=os.path.join("..",self.resources))
        subDir = os.path.join(self.outputdir,sub.name)

        if not os.path.exists(subDir):
            os.mkdir(subDir)
        f = open(os.path.join(subDir,"index.html"), "w")
        f.write(output)

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
                                 styleDir=os.path.join(".",self.resources))

        f = open(os.path.join(self.outputdir,"index.html"), "w")
        f.write(output)
        f.close()

        self.addResources()

    def addResources(self):
        resDir = os.path.join(self.outputdir,self.resources)
        if not os.path.exists(resDir):
            os.mkdir(resDir)
        startDir = os.path.join(".", self.resources)
        src_files = os.listdir(startDir)

        for file_name in src_files:
            full_file_name = os.path.join(startDir, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, os.path.join(resDir, file_name))


