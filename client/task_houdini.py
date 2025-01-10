# -*- coding: utf-8 -*-
import dutil
from .taskbase import  TaskBase
from parameter.core import Parameter

class TaskHoudini(TaskBase):

    def __init__(self):
        super(TaskHoudini,self).__init__()
        self.taskType = 'houdini'
        self.title = 'houdini task'
        self.version = Parameter('18.0',widget='combobox',items=['18.0','17.0'])
        self.rop = Parameter('',widget='lineedit')
        self.tags = ['houdini']
        self.addEnv('HSITE=<path/to/your/HSITE>')

        self.setVisible('serialSubTasks', False)

    def makeTask(self):
        assert 0, 'houdini in tractor is not avalable.'

    def dlMakeTask(self, batchInfo):
        jobInfo = self.dlSetupJobInfo('Houdini', batchInfo)
        # jobInfo.Frames = ''
        # jobInfo.ChunkSize = 1000000

        pluginInfo = {
            "Build": None,
            "IFD": "",
            "IgnoreInputs": False,
            "Output": "",
            "OutputDriver": self.rop,
            "SceneFile": self.fileName,
            "Version": self.version
        }

        new_job = self.dlSubmit(jobInfo, pluginInfo)
        return new_job
