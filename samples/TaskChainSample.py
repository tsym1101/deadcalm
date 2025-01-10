# -*- coding: utf-8 -*-

import sys
import os
from PySide2 import QtWidgets
from client.bastionwindow import BastionWindow
from client.jobbase import JobBase
from client.task_maya import  TaskMaya
from client.task_nuke import  TaskNuke
from client.task_custom import TaskCustom
from client.taskbase import TaskBase
from global_config import loadConfig
import pprint

def makeTaskChainSample():

    job = JobBase() # Root Job
    job.title = 'test job'
    job.priority = 55
    job.projects = ["test_project"]
    #job.serialSubtasks = False  #defalut True

    #maya****************
    taskMaya = TaskMaya()
    taskMaya.title = 'maya task test'
    taskMaya.projectFolder = 'projects/test'
    taskMaya.fileName = 'foo.mb'
    taskMaya.start = 1
    taskMaya.end = 20
    taskMaya.service = []

    pprint.pprint(taskMaya.__dict__)

    #nuke****************
    taskNuke = TaskNuke()
    taskNuke.title = 'nuke test'
    taskNuke.fileName = 'aaa.nk'

    pprint.pprint(taskNuke.__dict__)

    #custom**************
    taskCustom = TaskCustom()
    taskCustom.title = 'my custom task'
    taskCustom.executable = taskCustom.appendD('mayabatch')
    taskCustom.envkey = ['maya2018']
    taskCustom.option = ['-proj','aaaaaa','aaa.mb']

    pprint.pprint(taskCustom.__dict__)

    # nested tasks *********************************************
    taskRoot = TaskBase()  # empty task (group task)
    taskRoot.title = 'root'
    taskParent = TaskBase()
    taskParent.title = 'parent'
    taskChild1 = TaskCustom()
    taskChild1.executable = 'cmd.exe'
    taskChild1.title = "child1"
    taskChild2 = TaskCustom()
    taskChild2.title = "child2"
    taskChild2.executable = 'cmd.exe'
    taskParent.addChild(taskChild1)
    taskParent.addChild(taskChild2)
    taskRoot.addChild(taskParent)

    # If True, Children tasks will be executed sequentially. If False,Executed in parallel
    taskRoot.serialSubTasks = True

    #add to job *******************************************************
    job.addChild(taskMaya)
    job.addChild(taskNuke)
    job.addChild(taskCustom)
    job.addChild(taskRoot)

    return job

def run_cli():
    job = makeTaskChainSample()
    job.submit()

def run_gui():
    app = QtWidgets.QApplication(sys.argv)
    job = makeTaskChainSample()
    window = BastionWindow(job=job)
    window.showMaximized()
    app.exec_()

if __name__ == '__main__':
    loadConfig(f'{os.path.dirname(__file__)}/../config.default.json')
    loadConfig(f'{os.path.dirname(__file__)}/../config.json')

    run_gui() # submit via gui.
    # run_cli() # submit a job directly.