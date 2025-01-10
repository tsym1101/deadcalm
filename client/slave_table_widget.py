# -*- coding: utf-8 -*-

#Qt resources.

import dutil

from PySide2.QtWidgets import*
from PySide2.QtGui import*
from PySide2.QtCore import*

from global_config import g_config
from aws import ec2_manager_client
from client import slaveinfo
import traceback
import pprint

import re

class SlaveTableWidget(QTableWidget):

    client = None
    tUtil = None

    def __init__(self,onPremise=True,parent=None):
        super(SlaveTableWidget, self).__init__(parent=parent)

        self.timer = QTimer(self)
        self.timeSpan = g_config.time_span * 1000
        self.timer.timeout.connect(self.on_timer_timeOut)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSortingEnabled(True)
        self.verticalHeader().hide()
        self.currentSortColumn = 0

        # self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.nowRefreshing = False
        # self.refreshTable = self.refreshTableOnPremise

        if onPremise:
            self.refreshTable = self.refreshTableOnPremise
        else:
            self.refreshTable = self.refreshTableAws

        # if onPremise:
        self.refreshTable()

    def showEvent(self, event):
        self.refreshTable()
        self.timer.start(self.timeSpan)
        # self.sortByColumn(0)

    def closeEvent(self, event):
        self.timer.stop()

    def on_timer_timeOut(self):
        self.refreshTable()
        # dutil.logDebug('refresh')

    def getSelectedRowIndices(self):
        indices = []
        for model in self.selectionModel().selectedRows():
            row = model.row()
            indices.append(row)
        return indices

    def getSelectedRowItemTexts(self,col = 0):
        texts = []
        for model in self.selectionModel().selectedRows():
            row = model.row()
            item = self.item(row,col)
            if item:
                text = self.item(row, col).text()
            else:
                dutil.logWarn('item missing. ' + str(row) + ',' + str(col))
                continue

            texts.append(text)
        return texts

    def selectRowsByColumnTexts(self,colTexts,col = 0):
        selMode = self.selectionMode()
        self.clearSelection()
        self.setSelectionMode(QAbstractItemView.MultiSelection)
        itemNames = []
        for row in range(self.rowCount()):
            item = self.item(row,col)
            if item:
                itemNames.append(item.text())
            else:
                dutil.logWarn('item missing. '  + str(row) + ',' + str(col))

        for t in colTexts:
            if t in itemNames:
                self.selectRow(itemNames.index(t))
        self.setSelectionMode(selMode)

    def restoreSelected(self,oldSelectedHostNames):
        self.setSelectionMode(QAbstractItemView.MultiSelection)
        newItems = []
        for r in range(self.rowCount()):
            item = self.item(r, 0)
            newItems.append(item)

        for s in oldSelectedHostNames:
            for item in newItems:

                if item.text() == s:
                # p = re.compile(item.text(),re.IGNORECASE)
                # if p.match(s) != None:
                    self.selectRow(item.row())
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def refreshTableOnPremise(self):

        self.nowRefreshing = True
        selectedHostNames = self.getSelectedRowItemTexts()
        self.clear()
        scrollv = self.verticalScrollBar().value()
        scrollh = self.horizontalScrollBar().value()
        self.setSortingEnabled(False) #いったんオフにしないと表示が崩れる

        hHeaders = slaveinfo.SlaveInfo().keys()
        slaveInfos = slaveinfo.SlaveInfos()
        slaveInfos.correctInfos()

        self.setColumnCount(len(hHeaders))
        rowCount = len(slaveInfos.result)
        self.setRowCount(rowCount)
        self.setHorizontalHeaderLabels(hHeaders)

        row = 0
        for slave in slaveInfos.result:
            col = 0
            color = QColor(128, 128, 128)
            if slave['state'] == 'active':
                color = QColor(0, 255, 0)
            elif  slave['state'] == 'idle':
                color = QColor(0, 120, 220)

            # dutil.logInfo('slave:' + str(slave))

            for k in hHeaders:

                item = QTableWidgetItem(slave[k])
                item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
                item.setForeground(color)
                self.setItem(row,col,item)

                # if k == 'ip':
                #     dutil.logDebug('ip:' + slave[k] + ' col:' + str(col)  + ' row:' + str(row) + ' text:' + item.text())

                col += 1



            # self.setRowHeight(row, 20)
            row += 1

        self.restoreSelected(selectedHostNames)
        self.setSortingEnabled(True)
        self.sortByColumn(self.currentSortColumn,Qt.AscendingOrder)
        self.verticalScrollBar().setValue(scrollv)
        self.horizontalScrollBar().setValue(scrollh)
        self.nowRefreshing = False

    def refreshTableAws(self):

        if not SlaveTableWidget.client:
            serverHost = g_config.ec2_manager_ip[0]
            SlaveTableWidget.client = ec2_manager_client.ec2_manager_client(serverHost=serverHost)

        if SlaveTableWidget.tUtil == None:
            raise
            # SlaveTableWidget.tUtil = TractorUtil()

        self.nowRefreshing = True

        selectedHostNames = self.getSelectedRowItemTexts()
        self.clear()
        scrollv = self.verticalScrollBar().value()
        scrollh = self.horizontalScrollBar().value()
        self.setSortingEnabled(False) #いったんオフにしないと表示が崩れる

        killHeader = 'progress to kill (s)'

        hHeaders = slaveinfo.SlaveInfo().keys()
        hHeaders.append(killHeader)
        slaveInfos = slaveinfo.SlaveInfos()
        slaveInfos.correctInfos(onPremise=False,onDemandOnly=True)

        self.setColumnCount(len(hHeaders))
        rowCount = len(slaveInfos.result)
        self.setRowCount(rowCount)
        self.setHorizontalHeaderLabels(hHeaders)

        SlaveTableWidget.client.getCount()

        row = 0
        for info in slaveInfos.result:
            ip = info.ip
            countDown = g_config.kill_count * g_config.time_span
            if SlaveTableWidget.client.slaveActiveCounter.has_key(ip):
                countDown -= SlaveTableWidget.client.slaveActiveCounter[ip] * g_config.time_span
            else:
                # dutil.logError('not found tractor count status.' + ip + '\n')
                pass

            # 時間：分に変換
            m,s = divmod(countDown,60)
            time = '{:0=2}:{:0=2}'.format(m, s)
            if not info.state == 'idle':
                time = '-'

            # for slave in slaveInfos.result:
            col = 0
            color = QColor(128, 128, 128)
            if info['state'] == 'active':
                color = QColor(0, 255, 0)
            elif info['state'] == 'idle':
                color = QColor(0, 120, 220)

            for k in slaveinfo.SlaveInfo().keys():
                item = QTableWidgetItem(info[k])
                item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
                item.setForeground(color)
                self.setItem(row, col, item)
                col += 1

            #最後の１列(progress to kill)
            item = QTableWidgetItem(time)
            item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
            item.setForeground(color)
            self.setItem(row, col, item)
            # if not time == '-':
            #     dutil.logInfo('col:' + str(col) + 'row:' + str(row) + ' time:' + time + ' ip:' + ip)

            # self.setRowHeight(row, 20)
            row += 1

        self.restoreSelected(selectedHostNames)
        self.setSortingEnabled(True)
        self.sortByColumn(self.currentSortColumn,Qt.AscendingOrder)
        self.verticalScrollBar().setValue(scrollv)
        self.horizontalScrollBar().setValue(scrollh)
        self.nowRefreshing = False
