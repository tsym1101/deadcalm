# -*- coding: utf-8 -*-

import sys
import pprint
from orderedattrdict import AttrDict
import re
# from TractorUtil import TractorUtil
import dutil
from global_config import g_config

# import Deadline.DeadlineConnect as Connect
from client.taskbase import TaskBase

class SlaveInfo(AttrDict):
    def __init__(self):
        super(SlaveInfo, self).__init__()
        self.hostName = ''
        self.state ='none' #active or idle or none
        self.owner = ''
        self.os = ''
        self.gpu = ''
        self.ip = ''
        self.desc = ''
        self.numCpu = 0
        self.memory = 0
        self.version = ''

class SlaveInfos:
    tUtil = None

    def __init__(self):

        self.result = []

    def getStateByIp(self,ip):
        for info in self.result:
            if info.ip==ip:
                return info.state

    def correctInfos(self,onPremise=True,onDemandOnly=False):

        if g_config.use_deadline == True:

            TaskBase.initDeadLineConnection()
            conn = TaskBase.dl_conn
            dlSlaveInfos = conn.Slaves.GetSlaveInfos()

            if dlSlaveInfos and not onPremise and onDemandOnly:
                ondemand_ip_prefix = g_config.ondemand_ip_prefix
                max_ondemand_instance = g_config.max_ondemand_instance
                onDemandIps = []

                for row in range(max_ondemand_instance):
                    info = SlaveInfo()
                    ip = ondemand_ip_prefix + str(row)
                    hostName = 'ip-' + ip.replace('.','-')
                    info.hostName = hostName
                    info.ip = ip

                    for slave in dlSlaveInfos:
                        if slave['Name'] == hostName:
                            info.desc = slave['Msg']
                            info.ip = slave['IP']
                            info.state = 'none'
                            if slave['Stat'] == 1:
                                info.state = 'active'
                            elif slave['Stat'] == 2:
                                info.state = 'idle'
                            elif slave['Stat'] == 3:
                                info.state = 'offline'
                            elif slave['Stat'] == 4:
                                info.state = 'stalled'
                            else:
                                info.state = 'unknown'

                            dutil.logDebug('stat=' + str(slave['Stat']))
                            dutil.logDebug('info.state=' + str(info.state))

                            info.owner = str(slave['JobUser'])
                            info.numCpu = str(slave['Procs'])
                            info.memory = str(slave['RAM'])
                            # profile = blade['profile']
                            info.version = slave['Ver']
                            info.os = slave['OS']
                            info.gpu = slave['Vid']
                            break

                    self.result.append(info)
                return

            if dlSlaveInfos:
                for slave in dlSlaveInfos:
                    if re.match('ip-',slave['Name']) and onPremise:
                        continue

                    info = SlaveInfo()
                    info.hostName = str(slave['Name']).lower() #ADのマシン名が大文字になってしまうのでここで小文字に強制変換
                    info.desc = slave['Msg']
                    info.ip = slave['IP']

                    # dutil.logInfo('hostname:' + info.hostName + ' ip:' + info.ip)

                    info.state = 'none'
                    if slave['Stat'] == 1:
                        info.state = 'active'
                    elif slave['Stat'] == 2:
                        info.state = 'idle'
                    elif slave['Stat'] == 3:
                        info.state = 'offline'
                    elif slave['Stat'] == 4:
                        info.state = 'stalled'
                    else:
                        info.state = 'unknown'

                    info.owner = str(slave['JobUser'])
                    info.numCpu = str(slave['Procs'])
                    info.memory = str(slave['RAM'])
                    # profile = blade['profile']
                    info.version = slave['Ver']
                    info.os = slave['OS']
                    info.gpu = slave['Vid']

                    self.result.append(info)

                return

        else:
            if not SlaveInfos.tUtil:
                SlaveInfos.tUtil = TractorUtil()

            bladeInfo = SlaveInfos.tUtil.getAllBladeStatus()

            # for row in range(len(slaves)):
            #     info = SlaveInfo()
            #     hostName = slaves[row]
            #     info.hostName = hostName
            #
            #     if bladeInfo:
            #         for blade in bladeInfo:
            #             if blade['hnm'] == hostName:
            #                 info.desc = blade['note']
            #                 info.ip = blade['addr']
            #                 info.state = 'none'
            #
            #                 if blade['numcmd'] == 0:
            #                     info.state = 'idle'
            #                 else:
            #                     info.state = 'active'
            #
            #                 info.owner = str(blade['owners'])
            #                 info.numCpu = str(blade['ncpu'])
            #                 info.memory = str(round(blade['mem'], 2))
            #                 # profile = blade['profile']
            #                 info.version = blade['vers']
            #                 break
            #
            #     self.result.append(info)

            if bladeInfo:
                for blade in bladeInfo:
                    if re.match('ip-', blade['hnm']) and onPremise:
                        continue
                    info = SlaveInfo()
                    info.hostName = blade['hnm']
                    info.desc = blade['note']
                    info.ip = blade['addr']
                    info.state = 'none'

                    if blade['numcmd'] == 0:
                        info.state = 'idle'
                    else:
                        info.state = 'active'

                    info.owner = str(blade['owners'])
                    info.numCpu = str(blade['ncpu'])
                    info.memory = str(round(blade['mem'], 2))
                    # profile = blade['profile']
                    info.version = blade['vers']
                    self.result.append(info)




if __name__ == '__main__':
    slaveInfos = SlaveInfos()
    slaveInfos.correctInfos()
    pprint.pprint(slaveInfos.infos)

    print(SlaveInfo().keys())
