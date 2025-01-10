# -*- coding: utf-8 -*-
import dutil
from .taskbase import  TaskBase
#import tractor.api.author as author
import re

from parameter.core import Parameter

class TaskNuke(TaskBase):

    def __init__(self):
        super(TaskNuke,self).__init__()
        self.taskType = 'nuke'
        self.title = 'nuke task'
        self.version = Parameter('12.2v1',widget='combobox',items=['12.2v1'])
        self.setVisible('serialSubTasks', False)
        self.tags = ['nukex']

    def makeSingleTask(self,startFrame,endFrame):

        # if not self.valid():
        #     DebugUtil.logError('invalid status.')
        #     return None

        majorVersion = self.version.split('v')[0]
        bin = "C:/Program Files/Nuke" + self.version + "/Nuke" + majorVersion + ".exe";

        range = str(int(startFrame)) + '-' + str(int(endFrame))
        cmd = [bin,
               '-x',
               '-F',range,
               self.fileNameD()]

        if len(self.option) > 0:
            insert = len(cmd)-1
            cmd[insert:insert] = self.option

        trTask = author.Task()
        trTask.title = self.title

        trCommand = author.Command()
        trCommand.argv = cmd
        trCommand.service = self.getServiceAsTractorFormat()
        trTask.addCommand(trCommand)
        return trTask

    def makeTask(self):
        return self.makeMultiFrameTask()

    def dlMakeTask(self, batchInfo):
        jobInfo = self.dlSetupJobInfo('Nuke', batchInfo)

        version = self.version
        version = re.sub('v\d+$','',version)

        writeNode =''
        if '-X' in self.option:
            index = self.option.index('-X')
            writeNode = self.option[index + 1]

        pluginInfo = {
            'SceneFile': self.fileName,
            'NukeX': True,
            'WriteNode': writeNode,
            'Version':version
        }

        new_job = self.dlSubmit(jobInfo, pluginInfo)
        return new_job
