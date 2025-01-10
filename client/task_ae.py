# -*- coding: utf-8 -*-
import re

from client.taskbase import TaskBase
from parameter.core import Parameter

class TaskAe(TaskBase):

    def __init__(self):
        super(TaskAe,self).__init__()
        self.taskType = 'ae'
        self.title = 'ae task'
        self.tags = ['ae']

        self.serverNum = Parameter(5,widget='spinbox',min=1)
        self.setVisible('serialSubTasks', False)
        self.setVisible('frameRange', False)
        self.setVisible('taskSize', False)
        self.version = Parameter('15.1',widget='combobox',items=['15.1'])

    def makeTask(self):
        pass

    def dlMakeTask(self, batchInfo):
        self.start = 1
        self.end = self.serverNum
        self.taskSize = 1

        jobInfo = self.dlSetupJobInfo('CommandLine', batchInfo)
        version = self.version
        version = re.sub('v\d+$', '', version)

        split = version.split('.')
        if len(split) > 2:
            major = split[0]
            minor = split[1]
            version = float(major + '.' + minor)
        else:
            version = float(version)

        executable = "C:/Program Files/Adobe/Adobe After Effects " + "CC 2018" + "/Support Files/aerender.exe"
        option = "-project " + self.fileName

        pluginInfo = {
            'Shell': 'default',
            'ShellExecute': False,
            'StartupDirectory': '',
            'Executable': executable,
            'Arguments': option,
            'SingleFramesOnly': False
        }

        new_job = self.dlSubmit(jobInfo, pluginInfo)
        return new_job



