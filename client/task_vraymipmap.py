# -*- coding: utf-8 -*-
import dutil
from .taskbase import  TaskBase
#import tractor.api.author as author
import  os
import re
from parameter.core import Parameter

class TaskVrayMipmap(TaskBase):

    def __init__(self):
        super(TaskVrayMipmap,self).__init__()
        self.taskType = 'vraymipmap'
        self.title = 'vraymipmap task'
        self.version = Parameter('2020',widget='combobox',items=['2018','2020'])
        self.outDir = Parameter('',widget='file',dir=True)

    def makeTask(self):
        bin = "C:/Program Files/Chaos Group/V-Ray/Maya " + self.version +" for x64/bin/img2tiledexr.exe";

        dir = self.fileName #input dir path
        files = []
        for filename in os.listdir(dir):
            if os.path.isfile(os.path.join(dir, filename)):  # ファイル名のみ取得
                files.append(dir + '/' + filename)

        filter = [r".tif",r".tiff",r".png",r".tga",r".bmp",r".exr",r".jpg",r".hdr",r".sgi",r".psd"]
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
            oFileName = oDirPath + '/' + baseName + '.exr'

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
