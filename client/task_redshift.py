# -*- coding: utf-8 -*-
import dutil
from .taskbase import  TaskBase

from parameter.core import Parameter

class TaskRedshift(TaskBase):

    def __init__(self):
        super(TaskRedshift,self).__init__()
        self.taskType = 'redshift'
        self.title = 'redshift task'
        self.tags = ['redshift']
        self.version = Parameter('1',widget='combobox',items=['1'])
        self.imageOutputDir =Parameter('',widget='file',dir=True)
        self.cacheDir = Parameter('',widget='file',dir=True)

    def makeTask(self):
        assert 0, 'redshift in tractor is not avalable.'

    def dlMakeTask(self, batchInfo):
        jobInfo = self.dlSetupJobInfo('Redshift', batchInfo)

        pluginInfo = {
            "SceneFile": self.fileName,
            "Version": self.version
        }

        if self.imageOutputDir:
            pluginInfo['ImageOutputDirectory'] = self.imageOutputDir

        if self.cacheDir:
            pluginInfo['CacheDirectory'] = self.cacheDir

        new_job = self.dlSubmit(jobInfo, pluginInfo)
        return new_job
