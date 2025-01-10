# -*- coding: utf-8 -*-

import getpass
import platform
from orderedattrdict import AttrDict

class BatchInfo(AttrDict):
    def __init__(self):
        super(BatchInfo, self).__init__()
        self.batchName = ''
        self.priority = 50
        self.project = ''
        self.currentJobDependencies = ''

    def deepcopy(self):
        result = BatchInfo()
        for k,v in self.items():
            result[k] = v
        return result


class JobInfo(AttrDict):
    def __init__(self):
        super(JobInfo, self).__init__()

        self.Plugin = ""

        #General
        self.Frames = "1-10"
        self.Name = "untitled"
        self.Comment = ""
        self.Department = ""
        self.BatchName = ""
        self.UserName = getpass.getuser()
        self.MachineName = platform.node()
        self.Pool = ""
        self.SecondaryPool = ""
        self.Group = ""
        self.Priority = 50
        self.ChunkSize = 5
        self.ConcurrentTasks = 1
        self.LimitConcurrentTasksToNumberOfCpus = True
        self.OnJobComplete = "Nothing"
        self.SynchronizeAllAuxiliaryFiles = False
        self.ForceReloadPlugin = False
        self.Sequential = False
        self.SuppressEvents = False
        self.Protected = False
        self.InitialStatus = "Active"

        # Timeouts
        # self.MinRenderTimeSeconds = 0
        self.MinRenderTimeMinutes = 0
        # self.TaskTimeoutSeconds = 0
        self.TaskTimeoutMinutes = 0
        # self.StartJobTimeoutSeconds = 0
        self.StartJobTimeoutMinutes = 0
        self.InitializePluginTimeoutSeconds = 0
        self.OnTaskTimeout = "Error"
        self.EnableTimeoutsForScriptTasks = False
        self.EnableFrameTimeouts = False
        self.EnableAutoTimeout = False

        # Interruptible
        self.Interruptible = False
        # self.InterruptiblePercentage = 0
        # self.RemTimeThreshold = 0

        #Notifications

        #Machine Limit
        self.MachineLimit = 0
        # self.MachineLimitProgress = 50
        self.Whitelist = ""
        # self.Blacklist = ""

        #Limits
        self.LimitGroups = ""

        #Dependencies
        self.JobDependencies = ""
        self.JobDependencyPercentage = -1
        self.IsFrameDependent = False
        self.FrameDependencyOffsetStart = 0
        self.FrameDependencyOffsetEnd = 0
        self.ResumeOnCompleteDependencies = True
        self.ResumeOnDeletedDependencies = False
        self.ResumeOnFailedDependencies = False
        self.RequiredAssets = ""
        self.ScriptDependencies = ""

        #Failure Detection
        self.OverrideJobFailureDetection = False
        # self.FailureDetectionJobErrors = 0
        self.OverrideTaskFailureDetection = False
        # self.FailureDetectionTaskErrors = 0
        self.IgnoreBadJobDetection = False
        self.SendJobErrorWarning = False

        #Cleanup
        self.DeleteOnComplete = False
        self.ArchiveOnComplete = False
        self.OverrideAutoJobCleanup = False
        # self.OverrideJobCleanup = False
        # self.JobCleanupDays = False
        self.OverrideJobCleanupType = "ArchiveJobs"

        #Scheduling
        #Scripts
        #Event Opt-Ins
        self.EventOptIns = ''
        #Environment
        # self.EnvironmentKeyValue0=""
        # self.EnvironmentKeyValue1=""
        # self.EnvironmentKeyValue2=""
        # self.EnvironmentKeyValue3=""
        # self.EnvironmentKeyValue4=""
        #Job Extra Info
        self.ExtraInfo0 = "" #project name
        # self.ExtraInfo1 = ""
        # self.ExtraInfo2 = ""
        # self.ExtraInfo3 = ""
        # self.ExtraInfo4 = ""
        # self.ExtraInfo5 = ""
        # self.ExtraInfo6 = ""
        # self.ExtraInfo7 = ""
        # self.ExtraInfo8 = ""
        # self.ExtraInfo9 = ""
        #Task Extra Info Names
        #Output
        #self.OutputFilename0 = ""
        #self.OutputDirectory0 = ""
        #Tile Job
        #Maintenance Job
        self.MaintenanceJob = False
        self.MaintenanceJobStartFrame = 0
        self.MaintenanceJobEndFrame = 0
