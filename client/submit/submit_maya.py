# -*- coding: utf-8 -*-

import sys
import os

from client.bastionwindow import BastionWindow
from client.jobbase import JobBase
from client.taskbase import TaskBase
from client.task_maya import TaskMaya
from client.task_custom import TaskCustom
from client.task_runec2 import *
from client.task_sync import TaskSync
from client.task_vray import TaskVray
from client import taskfactory
from client.task_fsx_allocator import TaskFsxAllocator
from client.taskbase import PathMapInfo
from global_config import g_config
import gui_resources_rc

reload(taskfactory)
# from client.task_maya import TaskMaya

from client.submit import ec2_utils

from PySide2.QtWidgets import *
import shiboken2
from maya import OpenMayaUI
import maya.mel
import maya.cmds

ptr = OpenMayaUI.MQtUtil.mainWindow()
parent = shiboken2.wrapInstance(long(ptr), QWidget)

g_mayaProjDirDefault = ['scenes','images','sourceimages','compimages','houdini','vrscenes','cache','movies','scripts']

def getFileNameBase():
    fileName = maya.cmds.file(q=True, sn=True)
    fileNameBase, ext = os.path.splitext(os.path.basename(fileName))
    return fileNameBase

def getProjectName():
    mayaProjDir = maya.cmds.workspace(q=True, fn=True)
    projectNameSplit = mayaProjDir.split('/')
    return projectNameSplit[-1]

def getRenderer():
    renderer = maya.mel.eval("getAttr defaultRenderGlobals.currentRenderer")
    if renderer == 'mayaSoftware':
        renderer = 'file'
    elif renderer == 'mayaHardware':
        renderer = 'hw'
    elif renderer == 'mayaHardware2':
        renderer = 'hw2'
    elif renderer == 'vray':
        pass
    elif renderer == '_3delight':
        renderer = '3delight'
    elif renderer == 'MayaKrakatoa':
        renderer = 'kmy'
    elif renderer == 'redshift':
        pass
    return renderer

def genBasicMayaTask(taskSize=5,service=[]):
    mayaFileName = maya.cmds.file(q=True, sn=True)
    mayaProjDir = maya.cmds.workspace(q=True, fn=True)

    task = TaskMaya()
    task.title = 'Maya Render : ' + str(getFileNameBase())
    task.version = maya.cmds.about(v=True)
    task.projectFolder = mayaProjDir
    task.renderer = getRenderer()
    task.start = maya.mel.eval("getAttr defaultRenderGlobals.startFrame")
    task.end = maya.mel.eval("getAttr defaultRenderGlobals.endFrame")
    task.fileName = mayaFileName
    task.taskSize = taskSize
    task.service = service

    return task

def openBastionWindow(job):
    app = QApplication.instance()
    w = BastionWindow(job=job, parent=parent)
    w.showMaximized()
    sys.exit()
    app.exec_()

def submitSimpleMayaTask(taskSize=5,service=[]):
    task = genBasicMayaTask(taskSize=taskSize,service=service)

    job = JobBase()
    job.title = str(getFileNameBase())
    job.prioroty = 50
    job.projects = [str(getProjectName())]

    job.addChild(task)

    openBastionWindow(job)

def submitMayaTaskByRenderLayer(taskSize=5,service=[]):
    taskGroup = TaskBase().asGroupTask()
    taskGroup.title = str('Maya Render Layer : ')  + str(getFileNameBase())
    taskGroup.dGroup = 'elite'

    rl =  maya.cmds.ls(type='renderLayer')
    currentLayer = maya.cmds.editRenderLayerGlobals( query=True, currentRenderLayer=True )

    fileNameBase = str(getFileNameBase())
    for layer in rl:
        isRenderable = maya.cmds.getAttr(layer + '.renderable')
        if isRenderable:
            maya.cmds.editRenderLayerGlobals(currentRenderLayer=layer)
            layerName = maya.mel.eval("renderLayerDisplayName " + layer)
            task = genBasicMayaTask(taskSize=taskSize,service=service)
            task.title = str('layer : ' + layerName) + ' - ' + fileNameBase
            task.option = [str('-rl'),str(layerName)]
            task.start = maya.cmds.getAttr("defaultRenderGlobals.startFrame")
            task.end = maya.cmds.getAttr("defaultRenderGlobals.endFrame")
            task.renderer = getRenderer()
            taskGroup.addChild(task)
    maya.cmds.editRenderLayerGlobals(currentRenderLayer=currentLayer)

    job = JobBase()
    job.title = str(getFileNameBase() + ' by render layer')
    job.prioroty = 50
    job.projects = [str(getProjectName())]

    job.addChild(taskGroup)

    openBastionWindow(job)

#awsに送るvrscene生成タスク
def genPreprocessVrayAtAwsTask():
    taskPreProcess = TaskBase().asGroupTask()
    taskPreProcess.title = 'generate resources'
    taskPreProcess.serialSubTasks = True

    # ----------------------
    taskGenVrayScenes = TaskBase()
    taskGenVrayScenes.title = 'generate vrscene by render layer'
    taskGenVrayScenes.serialSubTasks = False

    renderableLayers = maya.mel.eval("btGetRenderableLayer(1)")
    vrsceneFullPath = maya.mel.eval("btGetVrsceneFullPath()");
    for rl in renderableLayers:
        option = ['-rl', rl, '-noRender', '-exportCompressed', '-exportFileName', vrsceneFullPath]
        taskGenVrscene = genBasicMayaTask()
        taskGenVrscene.title = 'gen vrscene : ' + rl
        taskGenVrscene.taskSize = taskGenVrscene.end  # 強制1タスク化
        taskGenVrscene.option = option
        taskGenVrscene.dGroup = 'vm'
        taskGenVrayScenes.addChild(taskGenVrscene)

    taskPreProcess.addChild(taskGenVrayScenes)

    return taskPreProcess

#AWSでまわるvrayタスクを生成
def genRenderVrayAtAwsTask():
    vrsceneFullPathList = maya.mel.eval("getVrsceneFullPathList()")
    for vrscenePath in vrsceneFullPathList:
        taskRenderVray = TaskVray()
        vrscenePathTmp = os.path.basename(vrscenePath)
        taskRenderVray.title = str('render vray at AWS : ' + vrscenePathTmp)
        taskRenderVray.taskSize = 3
        taskRenderVray.fileName = vrscenePath
        yield taskRenderVray

def getVrayUploadPaths():
    mayaProjDir = str(maya.cmds.workspace(q=True, fn=True))
    vrsceneFullPath = maya.mel.eval("btGetVrsceneFullPath()");

    vrsceneDir = os.path.dirname(vrsceneFullPath) + '/'
    sourceImagesDir = mayaProjDir + '/' + 'sourceimages/'
    vrayMeshPathList = maya.mel.eval("btGetVrayMeshPath()")

    return [vrsceneDir,sourceImagesDir] + vrayMeshPathList

def submitRenderVrayAtAwsTask(skipPreprocess=False,
                              priority=50,
                              amiNameParam=None,
                              fsxName=None,fsxCapacity=1200,with_export=True):

    projectName = str(getProjectName())
    fileNameBase = str(getFileNameBase()) #タイトル用

    #fsxNameがセットされていればアロケータを生成
    taskFsxAllocator = None
    if fsxName:
        taskFsxAllocator = TaskFsxAllocator()
        taskFsxAllocator.name = fsxName
        taskFsxAllocator.project = projectName
        taskFsxAllocator.capacity = fsxCapacity
        taskFsxAllocator.with_export = with_export

    #オンプレでまわる事前プロセス
    taskPreProcess = None
    if not skipPreprocess:
        taskPreProcess = genPreprocessVrayAtAwsTask()

    # アップロードするディレクトリ
    uploadPaths = getVrayUploadPaths()

    #AWS上でまわるレンダリングタスクのリスト
    taskRenderVrayList = genRenderVrayAtAwsTask()
    taskEc2 = ec2_utils.asEc2Task(tasks=taskRenderVrayList,
                                  projectName=projectName,
                                  instanceTypes=['c5.2xlarge', 'c4.2xlarge', 'm5.2xlarge', 'm4.2xlarge'],
                                  useSpot=True,
                                  amiNameParam=amiNameParam,
                                  taskFsxAllocator=taskFsxAllocator)
    ec2Tasks = [taskEc2]

    #ダウンロードするディレクトリ
    downloadPaths = maya.mel.eval("btGetRenderImageDirs()")

    taskRoot = ec2_utils.genAwsPipelineTask(
        ec2Tasks=ec2Tasks,
        projectName=projectName,
        preTasks=[taskPreProcess],
        uploadPaths=uploadPaths,
        downloadPaths=downloadPaths,
        postTasks=[],
        taskFsxAllocator=taskFsxAllocator)

    job = JobBase()
    job.title = fileNameBase + '@AWS'
    job.priority = priority
    job.projects = [projectName]

    job.addChild(taskRoot)

    openBastionWindow(job)

if __name__ == '__main__':
    # submitSimpleMayaTask()
    # submitMayaTaskByRenderLayer()
    submitRenderVrayAtAwsTask()
