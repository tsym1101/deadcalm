# -*- coding: utf-8 -*-
import sys
import argparse
import time
from aws.ec2_manager import ec2_manager
import dutil
from client.taskbase import TaskBase
import pprint

def addInstanceToGroup(instanceInfos,groupName,requestId=None):
    conn = TaskBase.dl_conn
    if instanceInfos:
        hostNames = []

        for instanceInfo in instanceInfos:
            hostName = instanceInfo['hostName']
            instanceType = instanceInfo['instanceType']
            lifecycle = instanceInfo['lifecycle']
            hostNames.append(hostName)

            info = {
                'Name':hostName,
                'Ex0':instanceType,
                'Ex1':lifecycle,
                'Ex2': False, #flag for termination. If True, entry to slaves list that will be  terminated.
                'EventOI': ['Stamp']
            }

            if requestId:
                info['Ex3'] = requestId

            msg = conn.Slaves.SaveSlaveSettings(info=info)
            if msg == 'Success':
                dutil.logInfo(hostName + ' : append instance info.')
            else:
                dutil.logError(hostName + ' : ' + msg)

        groupNames = conn.Groups.GetGroupNames()
        if groupName not in groupNames:
            msg = conn.Groups.AddGroup(groupName)
            if msg.find('Error') > -1:
                dutil.logError(msg)
                dutil.logError('group name : {}'.format(groupName))
                dutil.logError('group names : {}'.format(str(groupNames)))
            else:
                dutil.logDebug('deadline add group : ' + msg)
        conn.Slaves.AddGroupToSlave(slave=hostNames, group=groupName)  # 重複処理大丈夫

        dutil.logInfo('add deadline group : ' + groupName + ' : ' + str(hostNames))
    else:
        dutil.logError('empty infos. ' + groupName)

# def submitCleanupMyselfJob():
#     pass

if __name__ == "__main__":

    dutil.debug_level = 0

    parser = argparse.ArgumentParser(description='request spot fleet and handle deadline job.')
    parser.add_argument('-it','--instanceTypes',type=str,required=True,help='multiple instance types, comma seperated.')
    parser.add_argument('-c','--capacity',type=int,required=True,help='num of instance for launch.')
    parser.add_argument('-grp','--group',type=str,required=True,help='deadline group to assgin job.')
    parser.add_argument('-o','--owner',type=str,required=True,help='aws resource owner.')
    parser.add_argument('-p','--project',type=str,required=True,help='project name which use slaves.')
    parser.add_argument('--useSpot', action='store_true')
    parser.add_argument('--useSingleAZ', action='store_true',help='restrict availability zone ,if needed.  .')
    parser.add_argument('--amiNameParam',type=str,help='ami Name parameter to launch in smm.')

    args = parser.parse_args()
    instanceTypes = args.instanceTypes
    capacity = args.capacity
    groupName = args.group
    owner = args.owner
    project = args.project
    useSpot = args.useSpot
    useSingleAZ = args.useSingleAZ
    amiNameParam = args.amiNameParam

    instanceTypes = instanceTypes.split(',')
    if len(instanceTypes) == 0:
        dutil.logError('invalid ips.')
        sys.exit(99)

    server = ec2_manager()
    TaskBase.initDeadLineConnection()
    conn = TaskBase.dl_conn

    if useSpot:

        response = server.requestSpotFleet(instanceTypes=instanceTypes,capacity=capacity,
                                           amiNameParam=amiNameParam,owner=owner,project=project,useSingleAZ=useSingleAZ)
        if not response:
            dutil.logError('request faild.')
            sys.exit(101)

        requestId = response['SpotFleetRequestId']
        dutil.logInfo('requestId:' + requestId)

        if groupName:

            time.sleep(10)

            fleetState = ''
            while True:
                try:
                    instanceInfos = server.getSpotFleetInstances(requestId=requestId)
                except:
                    dutil.logInfo('request may be canceled. : ' + requestId)
                    break

                addInstanceToGroup(instanceInfos,groupName,requestId=requestId)#リクエストと並行してグループに追加

                fleetState = server.getSpotFleetActivityState(requestId)
                if not fleetState:
                    dutil.logError('get fleet state failed.')

                if fleetState == 'fulfilled':
                    instanceInfos = server.getSpotFleetInstances(requestId=requestId)
                    addInstanceToGroup(instanceInfos, groupName, requestId=requestId) #最後に一回処理

                    deadline_user = groupName.split('-')[0]
                    server.createDeadlineTagByRequestid(requestId=requestId,deadline_group=groupName)
                    break
                elif fleetState == 'cancelled' or fleetState == 'failed' or fleetState == 'cancelled_running' or fleetState == 'cancelled_terminating':#'submitted'|'active'|'cancelled'|'failed'|'cancelled_running'|'cancelled_terminating'|'modifying'
                    dutil.logInfo('request canceled. : ' + requestId)
                    break
                else:
                    dutil.logInfo('waiting request progress ...')
                    time.sleep(10)

    else: #use ondemand

        instanseType = ''
        if not len(instanceTypes) == 1:
            dutil.logWarn('only one instance type is acceptable.')
        instanseType =instanceTypes[0]

        instanceInfos = server.runOnDemandInstance(instance_type=instanseType,capacity=capacity
                                                   ,amiNameParam=amiNameParam,owner=owner,project=project,useSingleAZ=useSingleAZ)
        if not instanceInfos:
            dutil.logWarn('instance infos empty. may be no capacity. ')
            sys.exit(0)

        if groupName:

            addInstanceToGroup(instanceInfos, groupName)

            instanceIds = []
            for instanceInfo in instanceInfos:
                instanceIds.append(instanceInfo['instanceId'])

            server.createDeadlineTag(instanceIds=instanceIds,deadline_group=groupName)

        dutil.logInfo('create instances.****************')
        pprint.pprint(instanceInfos)
        dutil.logInfo('total' + str(len(instanceInfos)) + ' instances are launched. (' + str(len(instanceInfos)) + '/' + str(capacity) + ')' )

    sys.exit(0)
