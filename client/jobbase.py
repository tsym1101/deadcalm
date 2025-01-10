# -*- coding: utf-8 -*-



from pprint import pprint
import json
import copy
from  collections import OrderedDict
import codecs
import getpass
from hashids import Hashids
import datetime

from .taskbase import  TaskBase

from . import  taskfactory
from global_config import g_config
import sys
import dutil
# #import tractor.api.author as author
from client.jobinfo import BatchInfo
from client.taskbase import PathMapInfo
from parameter.core import Parameter
from parameter.core import ParamSet
import traceback


class TaskEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, TaskBase):
            return o.__dict__
        if isinstance(o, PathMapInfo):
            return o.__dict__
            # if isinstance(o.parentTask,TaskBase):
            #     taskTmp = copy.deepcopy(o)
            #     taskTmp.parentTask = o.parentTask.id
            #     return taskTmp.__dict__
            # elif isinstance(o.parentTask,JobBase):
            #     taskTmp = copy.deepcopy(o)
            #     taskTmp.parentTask = 'root'
            #     return taskTmp.__dict__
            # return o.__dict__
        # if isinstance(o, JobBase):
        #     return None
        # elif isinstance(o,TaskTable):
        #     return

        return super(TaskEncoder, self).default(o)

def myhook(dict):
    # dutil.logDebug('myhook')

    for key, value in dict.items():

        if isinstance(value, unicode):
            dict[key] = str(value) #unicode to str
        elif isinstance(value, list) and len(value) > 0 and isinstance(value[0],unicode):
            newList = []
            for v in value:
                newList.append(str(v))
            dict[key] = newList

        # if key == 'taskTable':
        #     continue
        elif key == 'subtasks':
            subtaskList = []
            for subtask in value: #subtask is dict.
                taskTmp = taskfactory.restoreTask(str(subtask['taskType']), subtask)
                dutil.logDebug('id=' + taskTmp.id)
                TaskBase.hashTable[taskTmp.id] = taskTmp
                subtaskList.append(taskTmp)

            dict[key] = subtaskList

        # elif key == 'parentTask':
        #     return None



    return dict # 他の型はdefaultのデコード方式を使用

class JobBase(ParamSet):

    def __init__(self):
        super(JobBase, self).__init__()

        # self.title = 'my job'
        # self.priority = 50
        # self.subtasks = []
        # self.serialSubtasks = True
        # self.projects = []

        self.title = Parameter('my job',widget='lineedit')
        self.projects = Parameter([], widget='option')
        self.priority = Parameter(50,widget='spinbox')
        self.serialSubtasks = Parameter(True,widget='checkbox')
        self.submitButton = Parameter(None,widget='pushbutton',alias='submit',
                                      stylesheet='''
                                      QPushButton {
                                      padding: 10px;
                                      padding-left: 20px;
                                      padding-right: 20px;
                                      min-height:20px ;
                                      max-height:100px ;
                                      min-width:20px ;
                                      max-width: 1000px;
                                      font-size:30px;   
                                      qproperty-icon:url(:/images/deadline.png);   
                                      }
                                      ''')



        self.subtasks = []




    def addChild(self,task):
        task.onPremise = True
        self.subtasks.append(task)
        task.parentTask = None

    def save(self,filePath):
        with codecs.open(filePath, 'w','utf-8') as f:
            json.dump(self.__dict__, f, indent=2, cls=TaskEncoder)

    def load(self,filePath):
        with codecs.open(filePath, 'r','utf-8') as f:
            TaskBase.clearTable()
            # json_dict = json.load(f,object_hook = myhook,object_pairs_hook= OrderedDict)
            json_dict = json.load(f,object_hook = myhook)
            self.__dict__.update(json_dict)

    def fromJsonString(self,jsonString):
        TaskBase.clearTable()
        jsonDict = None
        try :
            jsonDict = json.loads(jsonString)
        except :
            dutil.logError('json parse failed. : \n' + traceback.format_exc())
            return

        dictTmp = myhook(jsonDict)
        self.__dict__.update(dictTmp)

    def makeJob(self):
        pass

    def dlMakeJob(self):
        jobHash = Hashids(min_length = 8,
                          salt='self.title' + str(datetime.datetime.now()))
        encode = 1234
        id = jobHash.encode(encode)
        userName = getpass.getuser()
        batchName = self.title + ' [' + userName + '-' + id + ']'

        priority = self.priority
        project = ''
        if self.projects:
            project = self.projects[0]

        # jobAttr = AttrDict()
        # jobAttr.batchName = batchName
        # jobAttr.priority = priority
        # jobAttr.project = project
        # jobAttr.jobDependencies = ''

        batchInfo = BatchInfo()
        batchInfo.batchName = batchName
        batchInfo.priority = priority
        batchInfo.project = project

        jobPrev = None
        for t in self.subtasks:
            dlSubJob = None
            if self.serialSubtasks and jobPrev:
                batchInfo.currentJobDependencies = jobPrev['_id']
                dlSubJob = t.dlMakeTaskChain(batchInfo=batchInfo)
            else:
                batchInfo.currentJobDependencies = ''
                dlSubJob = t.dlMakeTaskChain(batchInfo=batchInfo)

            assert not isinstance(dlSubJob,str), dlSubJob

            jobPrev = dlSubJob

        return batchName

    def submit(self):

        if not g_config.use_deadline:
            try:
                user = getpass.getuser()
                jobId = self.makeJob().spool(owner=user)
                msg = "tractor job submitted.\n" + "job id : " + str(jobId)
                return True,msg
            except:
                return  False,traceback.format_exc()
        else:
            try:
                TaskBase.initDeadLineConnection()
                batchName = self.dlMakeJob()
                msg = "deadline job submitted.\n" + "job title : " + batchName
                return True,msg
            except:
                return False, traceback.format_exc()

    def asTcl(self):
        return  self.makeJob().asTcl()


if __name__ == '__main__':

    pass




