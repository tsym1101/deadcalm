# -*- coding: utf-8 -*-

import sys
import os
import re
import argparse

from client.bastionwindow import BastionWindow
from client.jobbase import JobBase
from client.taskbase import TaskBase
from client.task_ae import TaskAe
from PySide2 import QtWidgets

def openBastionWindow(job):
    app = QtWidgets.QApplication(sys.argv)  # アプリケーションインスタンス
    window = BastionWindow(job=job)
    window.showMaximized()
    app.exec_()

def getFfmpegOutputPath(writeFilePath):
    # [ ]をとる
    r = r"(\[)|(])"
    OutputPathTmp = re.sub(r, "", writeFilePath)
    print(OutputPathTmp)

    # (の前にある一つ以上の_と.)+####をとる
    rs = r"(_*)+(\.*)+#+"
    ffmpegOutputPath = re.sub(rs, "", OutputPathTmp)
    # 拡張子をmovに置き換え
    ext = os.path.splitext(ffmpegOutputPath)
    ffmpegOutputPath = ffmpegOutputPath.replace(ext[1], ".mov")
    print("ffmpegOutputPath = " + ffmpegOutputPath)

    # ####を0000に変更
    n = r"#+"
    startFrame = "0000"
    oneOfSequenceFile = re.sub(n,startFrame,OutputPathTmp)
    print(oneOfSequenceFile)

    return ffmpegOutputPath, oneOfSequenceFile


def submitAe(projectPath,projectName,version):
    projectPath = projectPath.replace('\\','/')
    task = TaskAe()
    task.title = 'aerender:' + projectName
    task.fileName = projectPath
    task.version = version
    task.taskSize = 1

    job = JobBase()
    job.title = 'aerender:' + projectName
    job.projects = [TaskBase.getProjectName(projectPath)]

    job.addChild(task)
    openBastionWindow(job)

def submitAeWithFFmpeg(jsonPath):
    f = open(jsonPath)
    data = f.read()
    j = JobBase()
    j.fromJsonString(data)
    #print("pops " + str(len(j.subtasks)))#num of subtasks
    openBastionWindow(j)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='submit ae to deadLine arguments.',add_help=True)
    parser.add_argument('-flag', '--flag', required=True, help='whether you submit nomal render or ffmpeg render')
    parser.add_argument('-name', '--projectName', required=False, help='AE projectName for nomal render.')
    parser.add_argument('-path', '--projectPath', required=False, help='AE projectPath for nomal render.')
    parser.add_argument('-ver', '--version', required=False, help='AE version for nomal render.')
    parser.add_argument('-jPath', '--jsonPath', required=False, help='intermediate json file for ffmpeg render.')

    args = parser.parse_args()
    flag = args.flag

    if(flag == '0'):
        projectName = args.projectName
        projectPath = args.projectPath
        version = args.version
        submitAe(projectPath,projectName,version)

    if(flag == '1'):
        jsonPath = args.jsonPath
        submitAeWithFFmpeg(jsonPath)



