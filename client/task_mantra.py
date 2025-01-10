# -*- coding: utf-8 -*-
import dutil
from .taskbase import TaskBase


class TaskMantra(TaskBase):

    def __init__(self):
        super(TaskMantra,self).__init__()
        self.taskType = 'mantra'
        self.title = 'mantra task'
        self.version = '17.0'
        self.tags = ['mantra']
        self.addEnv('HSITE=<path/to/your/HSITE>')

    def makeTask(self):
        assert 0, 'mantra in tractor is not avalable.'

    def dlMakeTask(self, batchInfo):
        jobInfo = self.dlSetupJobInfo('Mantra', batchInfo)

        pluginInfo = {
            "CommandLineOptions": ' '.join(self.option),
            "OutputFile": "",
            "SceneFile": self.fileName,
            "Thread": 0,
            "Version": self.version
        }

        new_job = self.dlSubmit(jobInfo, pluginInfo)
        return new_job
