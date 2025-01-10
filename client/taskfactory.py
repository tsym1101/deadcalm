from error import *
#******************
from .taskbase import  TaskBase
from .task_maya import  TaskMaya
from .task_nuke import  TaskNuke
from .task_ae import  TaskAe
from .task_custom import  TaskCustom
from .task_vraymipmap import  TaskVrayMipmap
from .task_tdlmake import  TaskTdlMake
from .task_ffmpeg import  TaskFfmpeg
from .task_houdini import  TaskHoudini
from .task_mantra import  TaskMantra
from .task_redshift import  TaskRedshift
from .task_hengine import  TaskHengine
from .task_blender import  TaskBlender
from .task_vray import  TaskVray
from .task_sync import  TaskSync
#******************

from .itaskwidget import TaskPanel

from PySide2.QtGui import*

def getWidget(task):
    return TaskPanel(task)

tasks = {
    'empty':{'class':TaskBase,'icon':':images/qblock.png'},
    'maya': {'class': TaskMaya, 'icon': ':images/maya.png','hotkey':'Alt+M'},
    'nuke': {'class': TaskNuke, 'icon': ':images/nuke.png','hotkey':'Alt+N'},
    'ae': {'class': TaskAe, 'icon': ':images/aftereffects.png','hotkey':'Alt+A'},
    'custom': {'class': TaskCustom, 'icon': ':images/custom.png'},
    'vraymipmap': {'class': TaskVrayMipmap, 'icon': ':images/kinoko.png'},
    'tdlmake': {'class': TaskTdlMake, 'icon': ':images/kinoko.png'},
    'ffmpeg': {'class': TaskFfmpeg, 'icon': ':images/ffmpeg.png','hotkey':'Alt+F'},
    'houdini': {'class': TaskHoudini, 'icon': ':images/houdini.png'},
    'mantra': {'class': TaskMantra, 'icon': ':images/mantra.png'},
    'redshift': {'class': TaskRedshift, 'icon': ':images/redshift.png'},
    'hengine': {'class': TaskHengine, 'icon': ':images/hengine.png','hotkey':'Alt+H'},
    'blender': {'class': TaskBlender, 'icon': ':images/blender.png','hotkey':'Alt+B'},
    'vray': {'class': TaskVray, 'icon': ':images/vray.png','hotkey':'Alt+V'},
    'sync': {'class': TaskSync, 'icon': ':images/cloud-sync-icon.png','hotkey':'Alt+S'},
}

def getIcon(taskType):
    taskObj = tasks.get(taskType)
    if not taskObj:
        taskObj = tasks.get('empty')
    return QIcon(taskObj['icon'])

def restoreTask(taskType,subTaskDict):
    taskTmp = None
    taskObj = tasks.get(taskType)
    if taskObj is not None:
        taskTmp = taskObj['class']()
    else:
        raise TaskTypeNotFoundError(taskType)

    subtasksDictTmp = subTaskDict.get('subtasks')
    if subtasksDictTmp:
        subtasks = []
        for t in subtasksDictTmp:
            taskType = t['taskType']
            subTaskDictTmp = t
            subtask = restoreTask(taskType,subTaskDictTmp)
            subtasks.append(subtask)

        subTaskDict['subtasks'] = subtasks

    taskTmp.__dict__.update(subTaskDict)
    return taskTmp
