# -*- coding: utf-8 -*-

import sys
import copy
import os
from hashids import Hashids
from global_config import g_config
from . import jobinfo

import Deadline.DeadlineConnect as Connect

# #import tractor.api.author as author
import pprint

from .jobinfo import JobInfo
import dutil
import re
import traceback

from parameter.core import ParamSet
from parameter.core import Parameter

class PathMapInfo(object):
    def __init__(self):
        super(PathMapInfo, self).__init__()
        self.path = ''
        self.win = ''
        self.linux = ''
        self.mac = ''
        self.region = 'All'

# class TaskBase(object):
class TaskBase(ParamSet):

    # pushService = QtCore.Signal(str)
    hashTable = {}
    dl_conn = None

    @staticmethod
    def clearTable():
        TaskBase.hashTable.clear()

    @staticmethod
    def initDeadLineConnection():
        if not TaskBase.dl_conn:
            try:
                value = g_config.deadline_webservice
                TaskBase.dl_conn = Connect.DeadlineCon(value[0], int(value[1]))
                TaskBase.dl_conn.Slaves.GetSlaveInfos()
            except Exception as e:
                dutil.logError('deadline webservice : \n' + traceback.format_exc())
                exit(5)

    @staticmethod
    def getRepositoryPath():
        try:
            TaskBase.initDeadLineConnection()
            repoPath = TaskBase.dl_conn.Repository.GetRootDirectory()
            if os.name == 'posix':
                pass
            elif os.name == 'nt':
                repoPath = repoPath.replace(g_config.deadline_repository_path_posix,
                                            g_config.deadline_repository_path_nt)

            return repoPath
        except:
            dutil.logError('getRepositoryPath failed : \n' + traceback.format_exc())

    #旧メンバー変数の利用を警告するために定義
    def __setattr__(self, name, value):

        match = re.search(r'^dEnvironmentKeyValue[0-9]', name)
        if match:
            raise AttributeError('{} "{}": dEnvironmentKeyValue* in TaskBase is deprecated. Use TaskBase.addEnv(env="key=value") function.'.format(type(self).__name__,self.title))

        match = re.search(r'^dOutputDirectory[0-9]', name)
        if match:
            raise AttributeError(
                '{} "{}": dOutputDirectory* in TaskBase is deprecated. Use dOutputDirectories.'.format(
                    type(self).__name__, self.title))

        match = re.search(r'^dOutputFilename[0-9]', name)
        if match:
            raise AttributeError(
                '{} "{}": dOutputFilename* in TaskBase is deprecated. Use dOutputFilenames.'.format(
                    type(self).__name__, self.title))

        # object.__setattr__(self, name, value)

        if name == 'start':
            self.frameRange[0] = value
            return
        if name == 'end':
            self.frameRange[1] = value
            return

        super(TaskBase, self).__setattr__( name, value)

    def __getattribute__(self, name):
        if name == 'start':
            return self.frameRange[0]
        if name == 'end':
            return self.frameRange[1]
        return super(TaskBase, self).__getattribute__(name)


    def __init__(self):
        super(TaskBase, self).__init__()

        self.taskType = 'empty'
        # self.title = 'empty task'
        # self.start = 1
        # self.end = 10
        # self.taskSize = 5
        # self.fileName = ''
        # self.option = []

        self.envkey = []
        self.tags = []
        self.service = []
        # self.serialSubTasks = False

        self.title = 'empty task'
        # self.start = 1
        # self.end = 10
        self.frameRange = Parameter([1,10],widget='spinboxarray')
        self.taskSize = Parameter(5, widget='spinbox',min=1)
        self.fileName = Parameter('',widget='file')
        self.serialSubTasks = Parameter(False, widget='checkbox',visble=False)
        self.option = Parameter([], widget='option')

        self.parentTask = None
        self.subtasks = []
        self.onPremise = True

        self.dGroup = '' #deadline only
        self.dPool = '' #deadline only

        self.dComment = Parameter('',widget='lineedit',category='deadline common')
        self.dTaskTimeoutMinutes = Parameter(0, widget='spinbox', min=0, category='deadline common')
        self.dConcurrentTasks = Parameter(1, widget='spinbox', min=1, category='deadline common')
        self.dEventOptIns = Parameter('',widget='lineedit',category='deadline common')
        self.dOverrideJobFailureDetection = Parameter(False, widget='checkbox',category='deadline common')
        self.dFailureDetectionJobErrors = Parameter(1, widget='spinbox',min=0,category='deadline common')
        self.dInitialStatus = Parameter('Active',widget='combobox',items=['Active','Suspended'],category='deadline common')
        self.dPreJobScript = Parameter('',widget='lineedit',category='deadline common')
        self.dPreTaskScript = Parameter('',widget='lineedit',category='deadline common')
        self.__dEnvironmentKeyValues = Parameter([],widget='listwidget',category='deadline common',alias='EnvironmentKeys [key=value]',item_text='key=value')
        self.dOutputDirectories = Parameter([], widget='listwidget', category='deadline common',
                                            item_text='/path/to/directory')
        self.dOutputFilenames = Parameter([], widget='listwidget', category='deadline common',
                                          item_text='filename')

        self.pathMapInfoList = []

        #pathMapModeを使うには、共通のmappingの設定を、リポジトリPathMapの設定をsubmission time ruleに記述する。
        #submission time ruleに記述すると、サブミットしたjobに共通mappingが追加される。pathMapModeは、共通mappingがにどうやってカスタムmappingを追加するかのフラグ。
        self.pathMapMode = 'replace'  #pathMapMode=replace|insert|append

        # self.affectsService = [] #固有TaskIdのリスト

        hashids = Hashids(min_length=12,salt='bastion')
        encode=1234
        id = hashids.encode(encode)
        while id in TaskBase.hashTable:
            encode += 1
            id = hashids.encode(encode)
        self.id = id

        TaskBase.hashTable[id] = self

    def __del__(self):
        pass

    def destory(self):

        #消しながらfor in するのでコピー
        subtasksTmp = copy.deepcopy(self.subtasks)
        for s in subtasksTmp:
            s.destory()

        self.isolate()
        if self.id in TaskBase.hashTable:
            del TaskBase.hashTable[self.id]

    def getServiceAsTractorFormat(self):
        return str('|'.join(self.service))

    def addChild(self,task):
        task.onPremise = self.onPremise #基本は親を引き継ぐ
        self.subtasks.append(task)
        task.parentTask = self.id

    def isolate(self):
        if not self.parentTask:
            return
        parentTask = TaskBase.hashTable[self.parentTask]
        parentTask.subtasks.remove(self)
        self.parentTask = None

        dutil.logDebug('isolate!!!')

    def addTag(self,tag):
        if not tag in self.tags:
            self.tags.append(tag)

    def appendD(self,pathStr):
        return '%D(' + pathStr + ')'

    def makeTask(self):
        trTask = author.Task()
        trTask.title = str(self.title)
        trTask.serialsubtasks = self.serialSubTasks

        for st in self.subtasks:
            trTaskTmp = st.makeTask()
            trTask.addChild(trTaskTmp)

        return trTask

    #helper function for sequential task. ***************************
    def makeSingleTask(self,startFrame,endFrame):
        return author.Task(title = 'empty')

    def makeMultiFrameTask(self):
        totalFrame = self.end - self.start + 1
        taskCount  = int(totalFrame) / int(self.taskSize)

        startFrame = self.start
        endFrame = 0
        trTaskParent = author.Task()
        trTaskParent.title = str(self.title)
        trTaskParent.serialsubtasks = False

        for i in range(taskCount):
            endFrame = startFrame + self.taskSize - 1
            trTask = self.makeSingleTask(startFrame,endFrame)
            trTask.title =  str(self.title + ' [' + str(startFrame) + ' - ' + str(endFrame) + ']')
            trTaskParent.addChild(trTask)
            startFrame = endFrame + 1

        remainder = totalFrame % self.taskSize
        if not remainder == 0:
            endFrame = startFrame + remainder  - 1
            trTask = self.makeSingleTask(startFrame,endFrame)
            trTask.title = str(self.title + ' [' + str(startFrame) + ' - ' + str(endFrame) + ']')
            trTaskParent.addChild(trTask)

        return trTaskParent

    #****************************************************

    def fileNameD(self):
        return '%D(' + self.fileName + ')'

    # def affectsTo(self,task):
    #     self.affectsService.append(task.id)

    # def dlMakeTaskChain(self,priority,project,batchName,JobDependencies=None):
    def dlMakeTaskChain(self,batchInfo):

        if not self.subtasks:
            job = self.dlMakeTask(batchInfo)
            return job

        if self.serialSubTasks:
            for st in self.subtasks:
                subJob = st.dlMakeTaskChain(batchInfo)
                if subJob:
                    assert not isinstance(subJob,str), str(subJob)
                    batchInfo.currentJobDependencies = subJob["_id"]
        else:
            subTasksJobDependencies = []
            for st in self.subtasks:
                subJob = st.dlMakeTaskChain(batchInfo)
                # assert subJob, 'invalid job'
                if subJob:
                    assert not isinstance(subJob, str), str(subJob)
                    subTasksJobDependencies.append(subJob["_id"])
            subTasksJobDependencies = ','.join(subTasksJobDependencies)
            batchInfo.currentJobDependencies = subTasksJobDependencies

        thisJob = self.dlMakeTask(batchInfo)

        return thisJob

    def addEnv(self,env): #use
        self.__dEnvironmentKeyValues.append(env)
        assert len(self.__dEnvironmentKeyValues) < 10, '__dEnvironmentKeyValues must be less than 10.'

    def clearEnvs(self):
        self.__dEnvironmentKeyValues = []

    def getEnvs(self):
        return self.__dEnvironmentKeyValues

    def dlSetupJobInfo(self,pluginName,batchInfo):

        jobInfo = jobinfo.JobInfo()
        jobInfo.Plugin = pluginName
        jobInfo.Name = self.title

        if self.start == self.end:
            jobInfo.Frames = str(int(self.start))
        else:
            jobInfo.Frames = str(int(self.start)) + '-' + str(int(self.end))

        jobInfo.ChunkSize = self.taskSize
        jobInfo.JobDependencies = batchInfo.currentJobDependencies
        jobInfo.BatchName = batchInfo.batchName
        jobInfo.Priority = batchInfo.priority
        jobInfo.InitialStatus = self.dInitialStatus
        jobInfo.ExtraInfo0 = batchInfo.project
        jobInfo.ExtraInfo1 = self.taskType
        jobInfo.TaskTimeoutMinutes = self.dTaskTimeoutMinutes
        jobInfo.ConcurrentTasks = self.dConcurrentTasks
        jobInfo.LimitGroups = ','.join(self.tags)
        jobInfo.Comment = self.dComment
        jobInfo.PreJobScript = self.dPreJobScript
        jobInfo.PreTaskScript = self.dPreTaskScript

        for i in range(len(self.__dEnvironmentKeyValues)):
            jobInfo['EnvironmentKeyValue' + str(i)] = self.__dEnvironmentKeyValues[i]

        for i in range(len(self.dOutputDirectories)):
            jobInfo['OutputDirectory' + str(i)] = self.dOutputDirectories[i]

        for i in range(len(self.dOutputFilenames)):
            jobInfo['OutputFilename' + str(i)] = self.dOutputFilenames[i]

        self.dlAssignSlaves(jobInfo=jobInfo)

        jobInfo.EventOptIns = self.dEventOptIns

        if self.dOverrideJobFailureDetection:
            jobInfo.OverrideJobFailureDetection = self.dOverrideJobFailureDetection
            jobInfo.FailureDetectionJobErrors = self.dFailureDetectionJobErrors



        return jobInfo

    def dlMakeTask(self,batchInfo):

        if g_config.use_silhouette_plugin:
            jobInfo = self.dlSetupJobInfo('Silhouette',batchInfo)
            # force empty task
            jobInfo.Frames = 0  # force single task.
            jobInfo.Group = None
            jobInfo.Pool = None
            jobInfo.Whitelist = ''

            pluginInfo = {}
            new_job = self.dlSubmit(jobInfo, pluginInfo)
            return new_job
        else:
            return None

    def dlAssignSlaves(self,jobInfo): #whitelist,group,poolはこれで管理
        useWhiteList = True
        if self.dGroup:
            jobInfo.Group = self.dGroup
            jobInfo.Whitelist = ''
            useWhiteList = False
        if self.dPool:
            jobInfo.Pool = self.dPool
            jobInfo.Whitelist = ''
            useWhiteList = False

        if useWhiteList:
            whiteList = ",".join(self.service)
            jobInfo.Whitelist = whiteList

        # jobInfo.Group = ",".join(self.service)

    def dlSubmit(self,jobInfo, pluginInfo):
        job = TaskBase.dl_conn.Jobs.SubmitJob(jobInfo, pluginInfo)
        self.mapPath(job['_id'])
        return job


    def asGroupTask(self):
        self.service = []
        self.dPool = ''
        self.dGroup = ''
        self.start = 0
        self.end = 0

        self.hideAll()
        self.setVisible('serialSubTasks', True)

        return self


    def assignGroupToChildren(self,group):
        for st in self.subtasks:
            st.assignGroupToChildren(group)
            st.dGroup = group
            st.dEventOptIns = 'Stamp'

    @staticmethod
    def getProjectName(fileName):
        projectNameSplit = fileName.split(f'/{g_config.projects_root_dir_name}/')

        projectName = '' #Noneで返すと' '.joinできずにエラーになるので空文字で返す
        if len(projectNameSplit) > 1:
            projectName = projectNameSplit[1]
            if '/' in projectName:
                projectName = projectName.split('/')[0]
        return projectName

    @staticmethod
    def getProjectDir(fileName):
        projectNameSplit = fileName.split(f'/{g_config.projects_root_dir_name}/')
        projectDir = ''
        if len(projectNameSplit) > 1:
            projectName = projectNameSplit[1]
            if '/' in projectName:
                projectName = projectName.split('/')[0]
                projectDir = f'{projectNameSplit[0]}/{g_config.projects_root_dir_name}/{projectName}/'
        return projectDir

    def optionToOneLiner(self):
        optionTmp = []

        for o in self.option:
            o = o.strip()
            o = o.replace('"','\\"')
            find = re.findall(r'\s+',o)
            if find:
                o = '\"' + o + '\"'
            optionTmp.append(o)

        return ' '.join(optionTmp)

    def setAsOnetimeJob(self):
        self.dOverrideJobFailureDetection = True
        self.dFailureDetectionJobErrors = 1

    def addPathMapInfo(self,pathMapInfo):
        if not isinstance(pathMapInfo,PathMapInfo):
            dutil.logError('addPathMapInfo failed.')
            return
        self.pathMapInfoList.append(pathMapInfo)

    def mapPath(self,jobId):
        try:
            if not self.pathMapInfoList:
                return

            pathInfos = []
            for pathMapInfo in self.pathMapInfoList:
                if not pathMapInfo.path:
                    dutil.logWarn('mapPath invalid. do nothing. ' + jobId)
                    continue

                pathInfo = {
                    'Path':pathMapInfo.path,
                    'CaseSensitive': False,
                    'Region': pathMapInfo.region,
                    'RegularExpression': False
                }

                valid = False
                if pathMapInfo.win:
                    pathInfo['WindowsPath'] = pathMapInfo.win
                    valid = True
                if pathMapInfo.linux:
                    pathInfo['LinuxPath'] = pathMapInfo.linux
                    valid = True
                if pathMapInfo.mac:
                    pathInfo['MacPath'] = pathMapInfo.mac
                    valid = True

                if not valid:
                    dutil.logWarn('mapPath invalid. do nothing. ' + jobId)
                    continue

                pathInfos.append(pathInfo)

            if not pathInfos:
                return

            job = TaskBase.dl_conn.Jobs.GetJob(id=jobId)
            assert not isinstance(job, str), str(job)


            if self.pathMapMode=='insert':
                # pathInfosCurrent = ast.literal_eval(job['Props']['PathMap'])
                pathInfosCurrent = job['Props']['PathMap']
                pathInfos = pathInfos + pathInfosCurrent
                dutil.logInfo('inserted path mappting : ' + str(pathInfos))
            elif self.pathMapMode=='append':
                pathInfosCurrent = job['Props']['PathMap']
                pathInfos = pathInfosCurrent + pathInfos
                dutil.logInfo('appended path mappting : ' + str(pathInfos))
            elif  self.pathMapMode=='replace':
                pass
            else:
                assert 0 , 'unknown PathMap mode : ' + self.pathMapMode

            job['Props']['PathMap'] = pathInfos

            result = TaskBase.dl_conn.Jobs.SaveJob(jobData=job)

            if not result == 'Success' :
                dutil.logError('map path failed . ' + jobId)
        except:
            dutil.logError('map path failed : \n' + traceback.format_exc())

    def makeSuspended(self):
        self.dInitialStatus = 'Suspended'

    def makeActive(self):
        self.dInitialStatus = 'Active'

if __name__ == '__main__':
    jobInfo = JobInfo()
    pprint.pprint(jobInfo)
