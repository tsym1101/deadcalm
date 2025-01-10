# -*- coding: utf-8 -*-
import dutil
from .taskbase import  TaskBase
# import tractor.api.author as author

from parameter.core import Parameter

class TaskCustom(TaskBase):

    def __init__(self):
        super(TaskCustom,self).__init__()
        self.taskType = 'custom'
        self.title = 'custom task'
        self.withDistributeOption = Parameter(False,widget='checkbox')
        self.repStyle = Parameter('-s $s -e $e',widget='lineedit')
        self.executable = Parameter('c:/windows/system32/cmd.exe',widget='lineedit')

    def makeSingleTask(self, startFrame, endFrame):

        executable = self.executable.replace('\"',"")
        executable = executable.replace('\\',"/")

        rangeDesc = self.repStyle.replace('$s',str(startFrame))
        rangeDesc = rangeDesc.replace('$e',str(endFrame))

        rangeDesc = rangeDesc.split(' ') #to list

        cmd = [executable]
        cmd = cmd + rangeDesc + self.option

        trTask = author.Task()
        trTask.title = self.title + ' ' + str(startFrame) + '-' + str(endFrame)

        trCommand = author.Command()
        trCommand.argv = cmd
        trCommand.service = self.getServiceAsTractorFormat()
        trCommand.tags = self.tags

        dutil.logDebug(self.tags)

        trTask.addCommand(trCommand)
        return trTask

    def makeTask(self):

        if self.withDistributeOption == True:
            return self.makeMultiFrameTask()

        executable = self.executable.replace('\"',"")
        executable = executable.replace('\\',"/")

        cmd = [executable] + self.option

        trTask = author.Task()
        trTask.title = self.title

        trCommand = author.Command()
        trCommand.argv = cmd
        trCommand.tags = self.tags
        trCommand.service = self.getServiceAsTractorFormat()
        trTask.addCommand(trCommand)
        return trTask

    def dlMakeTask(self, batchInfo):
        jobInfo = self.dlSetupJobInfo('CommandLine', batchInfo)
        jobInfo.Frames = ''

        option = ""
        jobInfo.Frames = str(int(self.start))
        singleFramesOnly = True

        if self.withDistributeOption:
            jobInfo.Frames = str(int(self.start)) + '-' + str(int(self.end))
            jobInfo.ChunkSize = self.taskSize

            newOption =[]

            rangeDesc = self.repStyle.replace('$s', '<STARTFRAME>')
            rangeDesc = rangeDesc.replace('$e', '<ENDFRAME>')
            rangeDesc = rangeDesc.replace('\"','<QUOTE>')
            rangeDesc = rangeDesc.split(' ')  # to list

            for o in self.option:
                newO = o
                newO = newO.replace('\"', '<QUOTE>')

                # if newO.find(' ') > -1:
                #     newO = '<QUOTE>' + newO + '<QUOTE>'

                newOption.append(newO)

            newOption = rangeDesc + newOption + [self.fileName]
            # option = '\"' + " ".join(newOption) + '\"'
            option = " ".join(newOption)
            singleFramesOnly = False
        else:
            # option = " ".join(self.option)
            option = self.optionToOneLiner()
            option  = option.replace('\"', '<QUOTE>')

        pluginInfo = {
            'Shell': 'default',
            'ShellExecute': False,
            'StartupDirectory': '',
            'Executable': self.executable,
            'Arguments': option,
            'SingleFramesOnly' : singleFramesOnly
        }

        new_job = self.dlSubmit(jobInfo, pluginInfo)
        return new_job
