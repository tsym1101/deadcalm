# -*- coding: utf-8 -*-
import dutil
from .taskbase import  TaskBase
#import tractor.api.author as author

import re
from parameter.core import Parameter

class TaskSync(TaskBase):

    mode_enum = ['upload','download']

    def __init__(self):
        super(TaskSync,self).__init__()
        self.taskType = 'sync'
        self.title = 'sync task'
        self.pathMapMode = 'append'  # override default
        self.mode = Parameter('upload',widget='combobox',items=['upload','download'])
        self.storageType = Parameter('onpremise',widget='combobox',items=['onpremise','efs','s3'])

    def makeSingleTask(self,startFrame,endFrame):
        pass

    def makeTask(self):
        pass

    def dlMakeTask(self, batchInfo):

        jobInfo = self.dlSetupJobInfo('Sync', batchInfo)
        jobInfo.Frames = 0 #force single task.

        assert (self.mode=='upload' or self.mode=='download'), 'the mode param in sync task should be "upload|download".'

        option = " ".join(self.option)

        pluginInfo = {
            'TargetPath': self.fileName,
            'Mode' : self.mode,
            'Option' : option,
            'StorageType' : self.storageType
        }

        new_job = self.dlSubmit(jobInfo, pluginInfo)
        return new_job
