# -*- coding: utf-8 -*-

import sys
import os
import platform
import re
import argparse
import json

import dutil
from client.bastionwindow import BastionWindow
from client.jobbase import JobBase
from client.taskbase import TaskBase
from client.task_blender import TaskBlender
from client.task_fsx_allocator import TaskFsxAllocator
from client.submit import ec2_utils
from PySide2 import QtWidgets

def openBastionWindow(job):
    app = QtWidgets.QApplication(sys.argv)  # アプリケーションインスタンス
    window = BastionWindow(job=job)
    window.showMaximized()
    app.exec_()

def submitBlender(fileName,startFrame,endFrame,version, renderer):

    fileName = fileName.replace('\\','/')
    fileNameBase = os.path.basename(fileName)  # タイトル用
    
    task = TaskBlender()
    task.title = renderer + ':' + fileNameBase
    task.fileName = fileName
    task.start = int(startFrame)
    task.end = int(endFrame)
    task.version = version
    task.taskSize = 5

    print ('taskBlender.option {}'.format(task.option))

    job = JobBase()
    job.title = renderer + ':' + fileNameBase
    job.projects = [TaskBase.getProjectName(fileName)]

    job.addChild(task)
    openBastionWindow(job)


def genRenderBlenderAtAwsTask(fileName,startFrame,endFrame,version,renderer,taskSize=5):
    fileName = fileName.replace('\\', '/')
    fileNameBase = os.path.basename(fileName)  # タイトル用
    
    task = TaskBlender()
    task.title = renderer + ':' + fileNameBase
    task.fileName = fileName
    task.start = int(startFrame)
    task.end = int(endFrame)
    task.version = version
    task.taskSize = taskSize

    return [task]

def submitBlenderOnAws(fileName,startFrame,endFrame,version,renderer,
                       depends = [],
                       outputs = [],
                       taskSize=5,
                       skipPreprocess=False,
                       priority=50,
                       amiNameParam='/ec2-imagebuilder/deadline-docker-blender/latest',
                       fsxName=None,fsxCapacity=1200,with_export=True):
    fileName = fileName.replace('\\', '/')

    fileNameBase = os.path.basename(fileName) #タイトル用
    projectName = TaskBase.getProjectName(fileName)

    dutil.logDebug('projectName : {}'.format(projectName))
    dutil.logDebug('fileName : {}'.format(fileName))

    assert projectName , 'no project dir found.'

    #fsxNameがセットされていればアロケータを生成
    taskFsxAllocator = None
    if fsxName:
        taskFsxAllocator = TaskFsxAllocator()
        taskFsxAllocator.name = fsxName
        taskFsxAllocator.project = projectName
        taskFsxAllocator.capacity = fsxCapacity
        taskFsxAllocator.with_export = with_export

    # アップロードするディレクトリ
    uploadPaths = [fileName] + depends

    #AWS上でまわるレンダリングタスクのリスト
    taskRenderBlenderList = genRenderBlenderAtAwsTask(fileName,startFrame,endFrame,version,renderer,taskSize)

    taskEc2 = ec2_utils.asEc2Task(tasks=taskRenderBlenderList,
                                  projectName=projectName,
                                  instanceTypes=['g4dn.xlarge','g4dn.2xlarge','g3.4xlarge','g3s.xlarge'],
                                  useSpot=True,
                                  amiNameParam=amiNameParam,
                                  taskFsxAllocator=taskFsxAllocator)
    ec2Tasks = [taskEc2]

    taskRoot = ec2_utils.genAwsPipelineTask(
        ec2Tasks=ec2Tasks,
        projectName=projectName,
        preTasks=[],
        uploadPaths=uploadPaths,
        downloadPaths=outputs,
        postTasks=[],
        taskFsxAllocator=taskFsxAllocator)

    job = JobBase()
    job.title = fileNameBase + '@AWS'
    job.priority = priority
    job.projects = [projectName]

    job.addChild(taskRoot)

    openBastionWindow(job)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='submit ae to deadLine arguments.',add_help=True)
    parser.add_argument('-s', '--startFrame', required=True, help='Render start frame.')
    parser.add_argument('-e', '--endFrame', required=True, help='Render end frame.')
    parser.add_argument('-f', '--fileName', required=True, help='Blender fileName.')
    parser.add_argument('-ver', '--version', required=False, help='Blender version.')
    parser.add_argument('-r', '--renderer', required=False, help='Blender Render Engine.')
    parser.add_argument('--aws', action='store_true',default=False)
    parser.add_argument( '--depends', required=False, help='dependencies to be uploaded.')
    parser.add_argument( '--outputs', required=False, help='outputs to be downloaded.')

    args = parser.parse_args()

    fileName = args.fileName
    startFrame = args.startFrame
    endFrame = args.endFrame
    version = args.version
    renderer = args.renderer

    if not args.aws:
        submitBlender(fileName,startFrame,endFrame,version,renderer)
    else:
        depends = args.depends
        outputs = args.outputs
        depends = str(depends).split(',') if depends else []
        outputs = str(outputs).split(',') if outputs else []

        submitBlenderOnAws(fileName,startFrame,endFrame,version,renderer,
                           depends=depends,outputs=outputs)


