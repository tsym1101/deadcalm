# -*- coding: utf-8 -*-
import dutil
from .taskbase import  TaskBase
#import tractor.api.author as author
import  os
import re
from parameter.core import Parameter

class TaskTdlMake(TaskBase):

    def __init__(self):
        super(TaskTdlMake,self).__init__()
        self.taskType = 'tdlmake'
        self.title = 'tdlmake task'
        self.outDir = Parameter('',widget='file',dir=True)

    def makeTask(self):
        bin = "C:/Program Files/3Delight/bin/tdlmake.exe"

        dir = self.fileName #input dir path
        files = []
        for filename in os.listdir(dir):
            if os.path.isfile(os.path.join(dir, filename)):  # ファイル名のみ取得
                files.append(dir + '/' + filename)

        filter = [r".tif",r".tiff",r".png",r".tga",r".bmp",r".exr",r".jpg"]
        imagefiles = []
        for ext in filter:
            regStr =  str(ext + r'$')
            regex = re.compile(regStr)
            for name in files:
                if regex.search(name):
                    imagefiles.append(name)

        trTaskRoot = author.Task()
        trTaskRoot.title = self.title
        trTaskRoot.serialsubtasks = False

        dutil.logDebug(str(imagefiles))
        dutil.logDebug(str(files))

        for image in imagefiles:
            baseName, ext = os.path.splitext(os.path.basename(image))
            oDirPath = self.outDir
            oFileName = oDirPath + '/' + baseName + '.tdl.tiff'

            cmd = [bin]
            cmd = cmd + self.option + [image,oFileName]

            trTask = author.Task()
            trTask.title = str(self.title + ' ' + baseName)

            trCommand = author.Command()
            trCommand.argv = cmd
            trCommand.service = self.getServiceAsTractorFormat()
            trTask.addCommand(trCommand)
            trTaskRoot.addChild(trTask)

        return trTaskRoot

    def dlMakeTask(self,batchInfo):

        self.start = 0
        self.end = 0

        jobInfo = self.dlSetupJobInfo('CommandLine', batchInfo)

        bin = "C:/Program Files/3Delight/bin/tdlmake.exe"

        dir = self.fileName  # input dir path
        files = []
        for filename in os.listdir(dir):
            if os.path.isfile(os.path.join(dir, filename)):  # ファイル名のみ取得
                files.append(dir + '/' + filename)

        filter = [r".tif", r".tiff", r".png", r".tga", r".bmp", r".exr", r".jpg"]
        imagefiles = []
        for ext in filter:
            regStr = str(ext + r'$')
            regex = re.compile(regStr)
            for name in files:
                if regex.search(name):
                    imagefiles.append(name)

        # trTaskRoot = author.Task()
        # trTaskRoot.title = self.title
        # trTaskRoot.serialsubtasks = False

        thisTaskRoot = TaskBase()
        thisTaskRoot.title = 'tdlmake : ' + dir
        thisTaskRoot.serialSubTasks = False

        dutil.logDebug(str(imagefiles))
        dutil.logDebug(str(files))

        dependencies = []

        for image in imagefiles:

            jobInfo.Name = 'tdlmake : ' + os.path.basename(image)

            baseName, ext = os.path.splitext(os.path.basename(image))
            oDirPath = self.outDir
            oFileName = oDirPath + '/' + baseName + '.tdl.tiff'

            cmd = bin

            option = " ".join( self.option) + ' ' +  image + ' ' + oFileName

            pluginInfo = {
                'Shell': 'default',
                'ShellExecute': False,
                'StartupDirectory': '',
                'Executable': cmd,
                'Arguments': option,
                'SingleFramesOnly': True
            }

            new_job = self.dlSubmit(jobInfo, pluginInfo)

            dependencies.append(new_job['_id'])

        jobInfo = self.dlSetupJobInfo('CommandLine', batchInfo)
        jobInfo.Frames = 0

        CMD_APP = r'c:\windows\system32\cmd.exe'
        CMD_ARG = r'/c echo ' + self.title
        pluginInfo = {
            'Shell': 'default',
            'ShellExecute': False,
            'StartupDirectory': '',
            'Executable': CMD_APP,
            'Arguments': CMD_ARG,
            'SingleFramesOnly': True
        }

        jobInfo.JobDependencies = ','.join(dependencies)

        new_job = self.dlSubmit(jobInfo, pluginInfo)

        batchInfo.currentJobDependencies = new_job['_id']
        return new_job



