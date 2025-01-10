# -*- coding: utf-8 -*-
import dutil
from .taskbase import  TaskBase
#import tractor.api.author as author

import re


class TaskVray(TaskBase):

    def __init__(self):
        super(TaskVray,self).__init__()
        self.taskType = 'vray'
        self.title = 'vray task'
        self.version = '4'
        self.tags = ['vray']

    def makeSingleTask(self,startFrame,endFrame):
        pass

    def makeTask(self):
        pass

    def dlMakeTask(self, batchInfo):
        jobInfo = self.dlSetupJobInfo('Vray', batchInfo)

        pluginInfo = {
            'InputFilename': self.fileName
        }

        new_job = self.dlSubmit(jobInfo, pluginInfo)
        return new_job
