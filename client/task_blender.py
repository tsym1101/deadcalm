# -*- coding: utf-8 -*-
import dutil
from .taskbase import  TaskBase
#import tractor.api.author as author

import re

class TaskBlender(TaskBase):

    def __init__(self):
        super(TaskBlender,self).__init__()
        self.taskType = 'blender'
        self.title = 'blender task'

    def dlMakeTask(self, batchInfo):
        jobInfo = self.dlSetupJobInfo('Blender', batchInfo)

        pluginInfo = {
            'SceneFile': self.fileName,
            'Threads': 0,
            'Build':'64bit',
            # 'OutputFile': ''
        }

        new_job = self.dlSubmit(jobInfo, pluginInfo)
        return new_job
