# -*- coding: utf-8 -*-

import sys
import os
import nuke
import re
import dutil

from client.bastionwindow import BastionWindow
from client.jobbase import JobBase
from client.taskbase import TaskBase
from client.task_nuke import TaskNuke
from client.task_ffmpeg import TaskFfmpeg

from PySide2.QtWidgets import *
app = QApplication.instance()

def getFileNameBase(fileName):
    fileNameBase, ext = os.path.splitext(os.path.basename(fileName))
    return fileNameBase

def openBastionWindow(job):
    parentWidget = QApplication.activeWindow()
    w = BastionWindow(job=job,parent=parentWidget)
    w.showMaximized()

def getSelectedWriteNodes():
    selected = nuke.selectedNodes()
    if (len(selected) == 0):
        return None
    selectedNames = []
    for n in selected:
        if n.Class() == "Write":
            selectedNames.append(n.name())
    return selectedNames

def getWriteNode():
    selectWriteNodes = nuke.selectedNodes()
    #何も選択してなければ全WriteNodeを取得
    if len(selectWriteNodes) == 0:
        enableWriteNodes = []
        allWriteNodes = []
        allWriteNodes = nuke.allNodes("Write")
        for allWriteNode in allWriteNodes:
            if(allWriteNode["disable"].getValue()) != True:
                enableWriteNodes.append(allWriteNode)
        return enableWriteNodes
    #選択してればそのWriteNodeを取得
    else:
        enableWriteNodes = []
        for selectWriteNode in selectWriteNodes:
            if selectWriteNode.Class() == "Write":
                if selectWriteNode["disable"].getValue() != True:
                    enableWriteNodes.append(selectWriteNode)
        return enableWriteNodes
    return None


def getFfmpegOutputPath(writeFilePath,
                        toMoviesDir=False,
                        moviesDir=None):

    outputDir = None

    if toMoviesDir:
        baseName = os.path.basename(writeFilePath)
        regex = r'ep[0-9]{2,}s[0-9]{2,}c[0-9]{2,}'
        r = re.compile(regex)
        m = r.search(baseName)

        if not m:
            regex = r's[0-9]{2,}c[0-9]{2,}'
            r = re.compile(regex)
            m = r.search(baseName)

        if m:
            suffix = m.group(0) #epXXsXXcXXの部分
            # moviesDir =getMoviesDir(writeFilePath)
            if not moviesDir:
                raise ValueError("moviesDir must be specified")

            outputDir = moviesDir + '/' + suffix
            if not os.path.exists(outputDir):
                os.makedirs(outputDir)
                dutil.logInfo('mkdir:' + outputDir)
        else:
            dutil.logWarn('unmatch naming conventions. skipped. ' + writeFilePath)

    if not outputDir:
        # Nukeの書き出し先のひとつ上の階層を取得
        dirPath = os.path.dirname(writeFilePath)
        dirPathList = dirPath.split("/")
        outputDir = "/".join(dirPathList[0:len(dirPathList) - 1])

    # 書き出すファイル名と拡張子を取得
    fileName = os.path.basename(writeFilePath)
    ext = os.path.splitext(writeFilePath)
    # 拡張子をmovに置き換え
    fileName = fileName.replace(ext[1], ".mov")

    startFrame = nuke.root().knob('first_frame').value()

    regex = r'%0\dd'
    r = re.compile(regex)
    m = r.search(fileName)

    if m:
        suffix = m.group(0) #　%04dの部分を抽出
        numDigit = int(suffix.replace('%', '').replace('d', ''))
        writeFilePath = writeFilePath.replace(suffix, ("{0:0" + str(numDigit) + "d}").format(int(startFrame)))
        fileName = fileName.replace("_" + suffix, "")
        fileName = fileName.replace("." + suffix, "")

    ffmpegOutputPath = outputDir + "/" + fileName

    return ffmpegOutputPath, writeFilePath

def submitNuke(nuke_path=''):
    startFrame = int(nuke.root().knob('first_frame').value())
    endFrame = int(nuke.root().knob('last_frame').value())
    nkName = nuke.root().name()

    majorVersion = nuke.NUKE_VERSION_MAJOR
    minorversion = nuke.NUKE_VERSION_MINOR
    releaseVersion = nuke.NUKE_VERSION_RELEASE
    version = str(majorVersion) + '.' + str(minorversion) + 'v' + str(releaseVersion)

    fileNameBase = str(getFileNameBase(nkName))

    task = TaskNuke()
    task.title = str('Nuke render : ') + fileNameBase
    task.fileName = str(nkName)
    task.version = version
    task.start = startFrame
    task.end = endFrame
    task.taskSize = 10
    if nuke_path:
        nuke_path = nuke_path.replace('\\','/')
        task.addEnv('NUKE_PATH='+nuke_path)

    selectedWriteNodes = getSelectedWriteNodes()
    if selectedWriteNodes:
        task.option = [str('-X'),str(",".join(selectedWriteNodes))]

    job = JobBase()
    job.title = fileNameBase
    job.projects = [TaskBase.getProjectName(nkName)]

    job.addChild(task)

    openBastionWindow(job)

def submitNukeWithFFmpeg(taskSize=10,
                         toMoveisDir=False,
                         services=[]):

    startFrame = int(nuke.root().knob('first_frame').value())
    endFrame = int(nuke.root().knob('last_frame').value())

    # dutil.logDebug('end='+ str(endFrame))

    nkName = nuke.root().name()
    majorVersion = nuke.NUKE_VERSION_MAJOR
    minorversion = nuke.NUKE_VERSION_MINOR
    releaseVersion = nuke.NUKE_VERSION_RELEASE
    version = str(majorVersion) + '.' + str(minorversion) + 'v' + str(releaseVersion)

    fileNameBase = str(getFileNameBase(nkName))

    job = JobBase()
    job.title = fileNameBase
    job.projects = [TaskBase.getProjectName(nkName)]
    job.serialSubtasks = False

    writeNodes = getWriteNode()

    for writeNode in writeNodes:
        writeFilePath = writeNode["file"].getValue()
        ffmpegOutputPath, writeFilePath = getFfmpegOutputPath(writeFilePath,toMoviesDir=toMoveisDir)

        writeNodeName = str(writeNode["name"].getValue())

        taskGroup = TaskBase().asGroupTask()
        taskGroup.title = 'FFmpeg chain - ' + writeNodeName
        taskGroup.serialSubTasks = True
        taskGroup.dGroup = 'elite'

        taskNuke = TaskNuke()
        taskNuke.title = str('Nuke render : ') + writeNodeName + ' - ' + fileNameBase
        taskNuke.fileName = str(nkName)
        taskNuke.version = version
        taskNuke.start = startFrame
        taskNuke.end = endFrame
        taskNuke.taskSize = taskSize
        taskNuke.service = services
        taskNuke.option = [str('-X'), writeNodeName]

        taskFfmepg = TaskFfmpeg()
        taskFfmepg.title = 'FFmpeg : '  + writeNodeName + ' - ' + fileNameBase
        taskFfmepg.fileName = writeFilePath
        taskFfmepg.oFileName = ffmpegOutputPath
        taskFfmepg.start = startFrame
        taskFfmepg.end = endFrame
        taskFfmepg.autoFrameRange = False

        taskGroup.addChild(taskNuke)
        taskGroup.addChild(taskFfmepg)

        job.addChild(taskGroup)

    openBastionWindow(job)

if __name__ == "__main__":
    submitNuke()
