# -*- coding: utf-8 -*-

import sys
import os
import argparse
import time
from aws.ec2_manager import ec2_manager
import dutil
from global_config import g_config
from client.taskbase import TaskBase
import pprint
import codecs
import json
import traceback
import glob

if __name__ == "__main__":

    dutil.debug_level = 0

    parser = argparse.ArgumentParser(description='cleanup deadline job after rendering @aws.')
    # parser.add_argument('-rid','--requestId',type=str,required=False,help='requestId for cleanup.')
    parser.add_argument('-grp','--group',type=str,required=True,help='deadline group for cleanup.')
    parser.add_argument('-j', '--jobs', type=str, required=False,help='deadline jobs will be marked as complete , comma seperated.')

    args = parser.parse_args()
    groupName = args.group
    jobIdsTmp = args.jobs

    TaskBase.initDeadLineConnection()
    conn = TaskBase.dl_conn

    slaves = conn.Slaves.GetSlaveNamesInGroup(groupName)
    dutil.logDebug('slaves : '  + str(slaves))

    requestIds = []

    #cleanup spot###########################################################
    try:
        for hostName in slaves:
            slaveInfo = conn.Slaves.GetSlaveInfo(name=hostName)
            if slaveInfo and slaveInfo.has_key('Ex3'):
                requestId = slaveInfo['Ex3']
                if requestId and requestId not in requestIds:
                    requestIds.append(requestId)

        #cancel request
        if requestIds:
            jobIds = []
            jobIdsTmp = jobIdsTmp.split(',')
            for j in jobIdsTmp:
                if j not in jobIds:
                    jobIds.append(j)
            for jobId in jobIds:
                result = conn.Jobs.CompleteJob(id=jobId)
                dutil.logInfo('CompleteJob : ' + result + ' : ' + jobId)

            server = ec2_manager()
            for requestId in requestIds:

                fleetState = server.getSpotFleetActivityState(requestId)

                dutil.logInfo('fleet state : ' + fleetState + ' : ' + requestId)

                if fleetState:
                    response = server.cancelSpotFleetRequest(requestId=requestId)
                    if not response:
                        dutil.logError('cancel fleet faild.')
                        # sys.exit(101)

                    if len(response['UnsuccessfulFleetRequests']):
                        dutil.logError('fleet requests may be  unsuccessful. check console.')
                        pprint.pprint(response['UnsuccessfulFleetRequests'])

                    dutil.logInfo('cleanup fleet. ' + requestId)
                    pprint.pprint(response)

    except:
        dutil.logError(traceback.format_exc())

    #cleanup ondemand###########################################################
    if not requestIds:
        # dutil.logDebug('not requestIds : ' + str(not requestIds))
        # dutil.logDebug('requestIds : ' + str(requestIds))
        dutil.logInfo('start cleanup ondemand instances : ' + groupName)
        try:
            server = ec2_manager()
            for hostName in slaves:
                ip = hostName.replace('ip-','').replace('-','.')
                server.terminateSlaveInstance(ip=ip)
        except:
            dutil.logError(traceback.format_exc())

    msg = conn.Groups.DeleteGroup(name=groupName)
    dutil.logInfo('cleanup deadline group : ' + groupName + ' : ' + msg)

    sys.exit(0)
