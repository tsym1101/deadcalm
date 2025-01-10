# -*- coding: utf-8 -*-
import os
import sys

from collections import OrderedDict

#Qt resources.

import traceback
import argparse

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
# from PySide2.QtUiTools import*

from PySide2 import QtCore

from .ui.ui_BastionWindow import *
import version
from global_config import g_config
import dutil
from .jobbase import JobBase
from .taskbase import TaskBase
from . import taskfactory
from .taskflowitem import TaskFlowItem
from .flow_widget import TaskFlowWidget
from .slave_table_widget import SlaveTableWidget
from parameter.panel import Panel

class BastionWindow(QMainWindow, Ui_BastionWindow):
    def __init__(self,job = JobBase(),parent=None):
        super(BastionWindow, self).__init__(parent=parent)
        self.setupUi(self)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

        self.setWindowTitle('deadcalm v' + version.versionStr)
        icon = QIcon(":images/treasure_ship.png")
        self.setWindowIcon(icon)
        pixmapAlert = QPixmap(':images/bastion.png')

        self.setCentralWidget(None)

        self.dockWidgetConsole = QDockWidget("debug console", self)

        self.dockWidgetJob = QDockWidget("job", self)
        self.dockWidgetTask = QDockWidget("task", self)
        self.dockWidgetTaskFlow = QDockWidget("task flow", self)
        self.dockWidgetSlaves = QDockWidget("workers", self)

        #for disable to DockWidgetClosable
        self.dockWidgetJob.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.dockWidgetConsole.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.dockWidgetTask.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.dockWidgetTaskFlow.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.dockWidgetSlaves.setFeatures(QDockWidget.DockWidgetFloatable |QDockWidget.DockWidgetMovable)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidgetTask)
        self.splitDockWidget(self.dockWidgetTask,self.dockWidgetConsole,Qt.Vertical)
        self.splitDockWidget(self.dockWidgetTask,self.dockWidgetTaskFlow,Qt.Horizontal)
        self.splitDockWidget(self.dockWidgetTaskFlow,self.dockWidgetSlaves,Qt.Horizontal)
        self.splitDockWidget(self.dockWidgetConsole,self.dockWidgetJob,Qt.Horizontal)

        #**************************************************************************************************************


        self.consoleWidget = QWidget(self.dockWidgetConsole)
        self.verticalLayoutConsoleWidget = QVBoxLayout(self.consoleWidget)
        self.consoleWidget.setLayout(self.verticalLayoutConsoleWidget)
        self.dockWidgetConsole.setWidget(self.consoleWidget)

        self.QTextEditConsole = QTextEdit(':'.join(g_config.deadline_webservice), self.consoleWidget)
        self.QTextEditConsole.setFocusPolicy(Qt.ClickFocus)
        self.QTextEditConsole.setReadOnly(True)
        self.verticalLayoutConsoleWidget.addWidget(self.QTextEditConsole)

        self.taskWidget = QWidget(self.dockWidgetTask)
        self.verticalLayoutTaskWidget = QVBoxLayout(self.taskWidget)
        self.taskWidget.setLayout(self.verticalLayoutTaskWidget)
        self.dockWidgetTask.setWidget(self.taskWidget)

        self.taskFlowWidget = TaskFlowWidget(job,self.dockWidgetTaskFlow)
        self.dockWidgetTaskFlow.setWidget(self.taskFlowWidget)

        self.tableWidgetSlaves = SlaveTableWidget(self)

        self.widgetAlertLogo = QWidget(self.dockWidgetSlaves)
        self.labelSlavesAlert = QLabel(self.dockWidgetSlaves)
        self.labelSlavesAlertLogo = QLabel(self.widgetAlertLogo)
        self.labelSlavesAlert.setAlignment(Qt.AlignCenter)
        self.labelSlavesAlertLogo.setAlignment(Qt.AlignCenter)
        self.verticalLayoutWidgetAlertLogo = QVBoxLayout()
        self.verticalLayoutWidgetAlertLogo.addItem(QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.verticalLayoutWidgetAlertLogo.addWidget(self.labelSlavesAlert)
        self.verticalLayoutWidgetAlertLogo.addWidget(self.labelSlavesAlertLogo)
        self.verticalLayoutWidgetAlertLogo.addItem(QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.widgetAlertLogo.setLayout(self.verticalLayoutWidgetAlertLogo)
        self.labelSlavesAlertLogo.setPixmap(pixmapAlert)

        self.slaveWidget = QWidget(self)
        self.verticalLayoutSlaveWidget = QVBoxLayout(self.slaveWidget)
        self.verticalLayoutSlaveWidget.addWidget(self.tableWidgetSlaves)
        self.verticalLayoutSlaveWidget.addWidget(self.widgetAlertLogo)
        self.slaveWidget.setLayout(self.verticalLayoutSlaveWidget)
        self.dockWidgetSlaves.setWidget(self.slaveWidget)

        self.jobWidget = QWidget(self.dockWidgetJob)
        self.verticalLayoutJobWidget = QVBoxLayout(self.jobWidget)
        self.jobWidget.setLayout(self.verticalLayoutJobWidget)
        self.jobWidget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.dockWidgetJob.setWidget(self.jobWidget)

        self.jobPanel = Panel(job,self.jobWidget)
        self.verticalLayoutJobWidget.addWidget(self.jobPanel)
        job.param('submitButton').data = self.submit #assign callback function to submit button.

        self.jobWidget.setMinimumSize(QSize(400, 200))
        # self.consoleWidget.setMinimumSize(QSize(400, 200))
        self.taskWidget.setMinimumSize(QSize(450, 800))
        self.taskFlowWidget.setMinimumSize(QSize(300, 800))
        self.tableWidgetSlaves.setMinimumSize(QSize(350, 800))
        self.widgetAlertLogo.setMinimumSize(QSize(400, 0))

        self.firstTractorDashBoardLoaded = False
        self.createContextMenu()

        self.tableWidgetSlaves.itemSelectionChanged.connect(self.on_tableWidgetSlaves_itemSelectionChanged)

        self.taskFlowWidget.itemSelectionChanged.connect(self.on_taskFlowWidget_itemSelectionChanged)
        self.taskFlowWidget.itemChanged[TaskFlowItem, int].connect(self.on_taskFlowWidget_itemChanged)

        self.widgetAlertLogo.hide()

        self.currentWidget = None

        self.reset(job)

    def on_lineEditJobName_editingFinished(self):
        self.job.title = str(self.lineEditJobName.text())

    def on_lineEditProject_editingFinished(self):
        self.job.projects = [str(self.lineEditProject.text())]

    def on_spinBoxPriority_valueChanged(self,i):
        self.job.priority = i

    def setToGui(self,job):
        pass

    def reset(self,newJob):
        self.job = newJob

        layoutItem = self.verticalLayoutTaskWidget.takeAt(0)
        while layoutItem:
            if isinstance(layoutItem,QWidgetItem):
                w = layoutItem.widget()
                w.deleteLater()
                del layoutItem
            layoutItem = self.verticalLayoutTaskWidget.takeAt(0)

        self.taskFlowWidget.clear()

        if self.job:
            self.setupTaskFlowTree()

        self.setToGui(newJob)

    def newScene(self):
        TaskBase.clearTable()
        self.reset(JobBase())

    def createContextMenu(self):

        newAction = QAction('New', self)
        newAction.setShortcut('Ctrl+N')
        newAction.setStatusTip('New.')
        newAction.triggered.connect(self.newScene)

        saveStateAction = QAction('Save State', self)
        saveStateAction.setShortcut('Ctrl+S')
        saveStateAction.setStatusTip('save state.')
        saveStateAction.triggered.connect(self.save)

        loadStateAction = QAction('Load State',self)
        loadStateAction.setShortcut('Ctrl+O')
        loadStateAction.setStatusTip('load state.')
        loadStateAction.triggered.connect(self.load)

        self.menuFile.addAction(newAction)
        self.menuFile.addAction(saveStateAction)
        self.menuFile.addAction(loadStateAction)

        actionList = []

        class ActionCreater:
            def __init__(self,taskClass,bastionWindow):
                self.taskClass = taskClass
                self.bw = bastionWindow
            def add(self):
                task = self.taskClass()
                self.bw.job.addChild(task)
                self.bw.reset(self.bw.job)

        self.creaters = []

        for k,v in taskfactory.tasks.items():
            addTaskAction = QAction(k, self)
            if 'hotkey' in v:  # Updated line
                addTaskAction.setShortcut(v['hotkey'])
            # addTaskAction.setShortcut('Alt+G')
            addTaskAction.setStatusTip('add new {} task to task tree.'.format(k))

            creater = ActionCreater(taskClass=v['class'],bastionWindow=self)
            self.creaters.append(creater)

            addTaskAction.triggered.connect(creater.add)
            actionList.append(addTaskAction)

        self.menuAdd.addActions(actionList)

        self.useDeadLineAction = QAction('use deadline', self)
        self.useDeadLineAction.setStatusTip('use deadline.')
        self.useDeadLineAction.setCheckable(True)
        self.useDeadLineAction.triggered.connect(self.checkUseDeadLine)
        self.useDeadLineAction.setChecked(g_config.use_deadline)

        self.menuMisc.addAction(self.useDeadLineAction)

    def checkUseDeadLine(self):
        g_config.use_deadline = self.useDeadLineAction.isChecked()
        self.tableWidgetSlaves.refreshTable()
        dutil.logDebug('use deadline:' + str(g_config.use_deadline))

    def load(self):
        filePath = QFileDialog.getOpenFileName(self, 'select json file', filter="json (*.json)")
        fileName = filePath[0]
        if not fileName:
            return
        job = JobBase()
        TaskBase.clearTable()
        job.load(fileName)
        self.reset(job)
        dutil.logDebug('load : ' + fileName)

    def save(self):
        filePath = QFileDialog.getSaveFileName(self, 'json file', filter="json (*.json)")
        fileName = filePath[0]
        if not fileName:
            return
        self.job.save(fileName)
        dutil.logDebug('save : ' + fileName)

    def setupTaskFlowTree(self):
        self.taskFlowWidget.clear()
        self.taskFlowWidget.setColumnCount(1)
        for t in self.job.subtasks:
            widget = taskfactory.getWidget(t)
            if widget:
                #     self.verticalLayout_groupBoxTaskWidget.addWidget(widget)
                tfItem = TaskFlowItem(widget, parent=self.taskFlowWidget)
                self.setupSubTree(tfItem)
                self.taskFlowWidget.addTopLevelItem(tfItem)
        self.taskFlowWidget.expandAll()

        if len(self.job.subtasks):
            self.taskFlowWidget.topLevelItem(0).setSelected(True)

    def setupSubTree(self,taskFlowItem):
        task = taskFlowItem.getTask()
        for t in task.subtasks:
            widget = taskfactory.getWidget(t)
            if widget:
                tfItem = TaskFlowItem(widget, parent=self.taskFlowWidget)
                taskFlowItem.addChild(tfItem)
                self.setupSubTree(tfItem)
        taskFlowItem.setExpanded(True)

    def on_tableWidgetSlaves_itemSelectionChanged(self):
        hostNames = self.tableWidgetSlaves.getSelectedRowItemTexts(col=0)
        if self.currentWidget:
            self.currentWidget.getTask().service = hostNames

    def on_taskFlowWidget_itemChanged(self,taskFlowItem,column):
        taskFlowItem.getTask().title = taskFlowItem.text(column)
        dutil.logDebug('changed : ' + taskFlowItem.getTask().title)
    #
    def on_taskFlowWidget_itemSelectionChanged(self):
        selected = self.taskFlowWidget.selectedItems()

        if len(selected):
            if self.currentWidget:
                self.currentWidget.hide()

            taskFlowItem = selected[0]
            taskWidget = taskFlowItem.getWidget()

            self.verticalLayoutTaskWidget.insertWidget(0,taskWidget)
            self.currentWidget = taskWidget
            currentTask = taskWidget.getTask()

            self.dockWidgetTask.setWindowTitle('task : ' + currentTask.title)

            serviceKeys = currentTask.service
            hostNames = []
            for row in range(self.tableWidgetSlaves.rowCount()):
                hostNames.append(self.tableWidgetSlaves.item(row,0).text())

            #接続を外してitemSelectionのループ回避
            self.tableWidgetSlaves.itemSelectionChanged.disconnect(self.on_tableWidgetSlaves_itemSelectionChanged)
            self.tableWidgetSlaves.setSelectionMode(QAbstractItemView.MultiSelection)
            selected = False
            self.tableWidgetSlaves.clearSelection()

            for serviceKey in serviceKeys:
                if serviceKey in hostNames:
                    self.tableWidgetSlaves.selectRow(hostNames.index(serviceKey))
                    selected = True

            if not selected:
                self.tableWidgetSlaves.clearSelection()

            # ループ回避　ここまで
            self.tableWidgetSlaves.itemSelectionChanged.connect(self.on_tableWidgetSlaves_itemSelectionChanged)
            self.tableWidgetSlaves.setSelectionMode(QAbstractItemView.ExtendedSelection)

            # table widget 非表示化。ループ回避後にやらないとservice key が入れ替わってしまう。
            if currentTask.onPremise:
                self.widgetAlertLogo.hide()
                self.tableWidgetSlaves.show()
            else:
                self.tableWidgetSlaves.hide()
                alertComment = 'this task is managed dynamically after submitting the job.'
                self.labelSlavesAlert.setText(alertComment)
                self.widgetAlertLogo.show()
                self.currentWidget.show()
                return

            if not currentTask.dGroup:
                self.widgetAlertLogo.hide()
                self.tableWidgetSlaves.show()
            else:
                self.tableWidgetSlaves.hide()
                alertComment = 'deadline group assigned : ' + currentTask.dGroup
                self.labelSlavesAlert.setText(alertComment)
                self.widgetAlertLogo.show()
                self.currentWidget.show()
                return

            self.currentWidget.show()
        else:
            while self.verticalLayoutTaskWidget.count():
                child = self.verticalLayoutTaskWidget.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            # self.groupBoxTask.setTitle('task : *')
            self.dockWidgetTask.setWindowTitle('task : *')
            self.currentWidget = None

    def on_checkBoxViewTask_stateChanged(self,b):
        self.groupBoxTask.setVisible(b)

    def on_checkBoxViewTaskFlow_stateChanged(self,b):
        self.groupBoxTaskFlow.setVisible(b)

    def on_checkBoxViewSlaves_stateChanged(self,b):
        self.groupBoxSlaves.setVisible(b)

    def on_pushButtonReloadDashBoard_clicked(self):
        try:
            self.tractorDashBoard.reload()
        except:
            dutil.logError('disabled because Maya import problem.')


    def __del__( self ): # デストラクタ
        pass

    def submit(self):
        result,info = self.job.submit()
        if result:
            QMessageBox.information(None, "INFO",str('submit job\n' + self.job.title + ' : ' + str(info)), QMessageBox.Ok)
        else:
            QMessageBox.critical(None, "ERROR", "failed to submit.\n" + str(info), QMessageBox.Ok)

def run():
    parser = argparse.ArgumentParser(description='Bastion client window.')
    parser.add_argument('-v', '--verbose', type=int, default=1,
                        help='debug level. 0=debug 1=info(default) 2=warn 3=error 4=fatal')
    args = parser.parse_args()
    debugLevel = args.verbose
    app = QApplication(sys.argv)
    window = BastionWindow()

    window.showMaximized()

    app.exec_()

if __name__ == "__main__":
    run()
