# -*- coding: utf-8 -*-
import dutil
from .taskbase import  TaskBase

from parameter.core import Parameter

class TaskHengine(TaskBase):

    def __init__(self):
        super(TaskHengine,self).__init__()
        self.taskType = 'hengine'
        self.title = 'custom houdini engine task'
        self.version = Parameter('18.0.532',widget='combobox',items=['18.0.532'])
        self.renderNode = Parameter('',widget='lineedit')
        self.tags = ['houdini']
        self.frameIncrement = Parameter(1.0,widget='doublespinbox')
        self.wedgeNum = Parameter(-1,widget='spinbox',min=-1)
        self.addEnv('HSITE=<path/to/your/HSITE>')
        self.setVisible('serialSubTasks', False)

    def makeTask(self):
        assert 0, 'hengine in tractor is not avalable.'

    def dlMakeTask(self, batchInfo):
        jobInfo = self.dlSetupJobInfo('HEngine', batchInfo)
        # jobInfo.Frames = ''
        # jobInfo.ChunkSize = 1000000

        pluginInfo = {
            "SceneFile": self.fileName,
            "Version": self.version,
            "RenderNode": self.renderNode,
            "FrameIncrement":self.frameIncrement,
            "WedgeNum":self.wedgeNum
        }

        new_job = self.dlSubmit(jobInfo, pluginInfo)
        return new_job
