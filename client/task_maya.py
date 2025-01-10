# -*- coding: utf-8 -*-

import sys
import dutil
from client.taskbase import  TaskBase
from parameter.core import Parameter

class TaskMaya(TaskBase):

    renderer = ['file', 'vray', '3delight', 'kmy', 'redshift','hw2','hw']

    def __init__(self):
        # dutil.logDebug('type:'+type(self))
        super(TaskMaya,self).__init__()
        #super().__init__()
        self.taskType = 'maya'
        self.title = 'maya task'

        self.projectFolder = Parameter('',widget='file',dir=True)
        self.version = Parameter('2020',widget='combobox',items=['2018','2020'])
        self.renderer = Parameter('file',widget='combobox',items=TaskMaya.renderer)
        self.setVisible('serialSubTasks', False)

        self.setVisible('serialSubTasks',False)

        self.mayaBatch = False
        self.mayaBatchCommand = ''
        self.envkey = ['maya' + self.version]

    def valid(self):
        if not self.projectFolder:
            dutil.logError('empty project folder.')
            return False
        return True

    def makeSingleTask(self,startFrame,endFrame):

        if not self.valid():
            dutil.logError('invalid status.')
            return None

        cmd = [self.appendD('Render'),
               '-r',self.renderer,
               '-s', str(startFrame),
               '-e',str(endFrame),
               '-proj',self.appendD(self.projectFolder),
               self.fileNameD()]

        if len(self.option) > 0:
            insert = len(cmd)-1
            cmd[insert:insert] = self.option

        trTask = author.Task()
        # trTask.title = self.title

        trCommand = author.Command()
        trCommand.argv = cmd
        trCommand.envkey = self.envkey
        trCommand.service = self.getServiceAsTractorFormat()
        trCommand.tags = self.tags
        trTask.addCommand(trCommand)
        return trTask

    def addTagByRenderer(self):
        if self.renderer == 'mr':
            self.addTag('mentalray')
        elif self.renderer == 'vray':
            self.addTag('vray')
        elif self.renderer == '3delight':
            self.addTag('3delight')
        elif self.renderer == 'kmy':
            self.addTag('krakatoa')
        elif self.renderer == 'redshift':
            self.addTag('redshift')
        elif self.renderer == 'arnold':
            self.addTag('arnold')


    def makeTask(self):
        self.addTagByRenderer()
        return self.makeMultiFrameTask()

    def dlMakeTask(self, batchInfo):


        #MayaDev**************************************************************

        self.addTagByRenderer()

        jobInfo = self.dlSetupJobInfo('MayaDev', batchInfo)

        self.dlAssignSlaves(jobInfo=jobInfo)


        newOption = []

        for o in self.option:
            newO = o
            newO = newO.replace('\"', '<QUOTE>')
            newOption.append(newO)

        option = " ".join(newOption)
        singleFramesOnly = False

        pluginInfo = {
            'SceneFile': self.fileName,
            'Version': str(self.version),
            'ProjectDir': self.projectFolder,
            'Renderer': self.renderer,
            'Option': option,
            'SingleFramesOnly': singleFramesOnly
        }

        # if self.renderer == 'vray' and str(self.version) == '2020':
        #     jobInfo.EnvironmentKeyValue0 = 'VRAY_FOR_MAYA2020_MAIN_x64=C:/Progra~1/Autodesk/Maya2020/vray'
        #     jobInfo.EnvironmentKeyValue1 = 'VRAY_FOR_MAYA2020_PLUGINS=C:/Progra~1/Autodesk/Maya2020/vray/vrayplugins'
        #
        #     dutil.logInfo('this is vray.')
        # else :
        #     dutil.logInfo(self.renderer)
        #     dutil.logInfo(self.version)



        #preprocess for 3delight
        if self.renderer == '3delight':
            optionCurrent = pluginInfo['Option']
            pluginInfo['Option'] = optionCurrent + ' -tms 1 -an 1'
            jobInfo.Name = self.title + ' preprocess_for_3delight'
            jobInfo.Frames = str(int(self.start))

            preprocessJob = self.dlSubmit(jobInfo, pluginInfo)

            pluginInfo['Option'] = optionCurrent + ' -tms 0 -an 1'
            jobInfo.Name = self.title
            jobInfo.Frames = str(int(self.start + 1)) + '-' + str(int(self.end))
            jobInfo.JobDependencies = preprocessJob['_id']

        new_job = self.dlSubmit(jobInfo, pluginInfo)
        return new_job

if __name__ == '__main__':
    pass
