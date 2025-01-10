# -*- coding: utf-8 -*-
#Qt resources.
import gui_resources_rc

from PySide2.QtWidgets import*
from PySide2.QtGui import*
from PySide2.QtCore import*
from PySide2.QtUiTools import*

from client.ui.ui_DeadlineCommonWidget import *
import dutil

class DeadlineCommonWidget(QWidget, Ui_DeadlineCommonWidget):
    def __init__(self,task,parent=None):
        super(DeadlineCommonWidget, self).__init__(parent=parent)
        self.setupUi(self)
        self.task = task

        self.lineEditComment.editingFinished.connect(self.on_lineEditComment_editingFinished)
        self.spinBoxTaskTimeout.valueChanged[int].connect(self.on_spinBoxTaskTimeout_valueChanged)
        self.spinBoxConcurrentTasks.valueChanged[int].connect(self.on_spinBoxConcurrentTasks_valueChanged)
        self.listWidgetEnv.itemChanged.connect(self.on_listWidgetEnv_itemChanged)
        self.listWidgetOutputDir.itemChanged.connect(self.on_listWidgetOutputDir_itemChanged)

        self.pushButtonAddEnv.pressed.connect(self.on_pushButtonAddEnv_pressed)
        self.pushButtonDeleteEnv.pressed.connect(self.on_pushButtonDeleteEnv_pressed)
        self.pushButtonAddOutputDir.pressed.connect(self.on_pushButtonAddOutputDir_pressed)
        self.pushButtonDeleteOutputDir.pressed.connect(self.on_pushButtonDeleteOutputDir_pressed)


        # self.label_outdir.setText('outputdirs'.rjust(20))
        # self.label_env.setText('extra env key value'.rjust(20))
        #
        # self.label_outdir.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        # self.label_env.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        # custom_font = QFont()
        # custom_font.setPointSize(14)
        # self.label_outdir.setFont(custom_font)
        # self.label_env.setFont(custom_font)

        # expand = QSizePolicy.Preferred
        # self.label_outdir.setSizePolicy(expand,expand)
        # self.label_env.setSizePolicy(expand,expand)

        self.setToGui()

    def on_lineEditComment_editingFinished(self):
        self.task.dComment = self.lineEditComment.text()

    def on_spinBoxTaskTimeout_valueChanged(self,i):
        self.task.dTaskTimeoutMinutes = i

    def on_spinBoxConcurrentTasks_valueChanged(self,i):
        self.task.dConcurrentTasks = i

    def updateEnv(self):
        self.task.clearEnvs()
        for i in range(self.listWidgetEnv.count()):
            self.task.addEnv(self.listWidgetEnv.item(i).text())

    def updateOutputDir(self):
        self.task.dOutputDirectories=[]
        for i in range(self.listWidgetOutputDir.count()):
            self.task.dOutputDirectories.append(self.listWidgetOutputDir.item(i).text())

    def on_listWidgetEnv_itemChanged(self):
        self.updateEnv()
        dutil.logDebug(self.task.getEnvs())

    def on_listWidgetOutputDir_itemChanged(self):
        self.updateOutputDir()
        dutil.logDebug(self.task.dOutputDirectories)

    def on_pushButtonAddEnv_pressed(self):
        item = QListWidgetItem('key=value')
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        self.listWidgetEnv.addItem(item)

        self.updateEnv()

    def on_pushButtonDeleteEnv_pressed(self):
        item = self.listWidgetEnv.currentItem()
        self.listWidgetEnv.takeItem(self.listWidgetEnv.row(item))

        self.updateEnv()


    def on_pushButtonAddOutputDir_pressed(self):
        item = QListWidgetItem('path to output dir')
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        self.listWidgetOutputDir.addItem(item)

        self.updateOutputDir()

    def on_pushButtonDeleteOutputDir_pressed(self):
        item = self.listWidgetOutputDir.currentItem()
        self.listWidgetOutputDir.takeItem(self.listWidgetOutputDir.row(item))

        self.updateOutputDir()


    def setToGui(self):
        self.lineEditComment.setText(self.task.dComment)
        self.spinBoxTaskTimeout.setValue(self.task.dTaskTimeoutMinutes)
        self.spinBoxConcurrentTasks.setValue(self.task.dConcurrentTasks)

        for i in self.task.getEnvs():
            item = QListWidgetItem(i)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            self.listWidgetEnv.addItem(item)

        for i in self.task.dOutputDirectories:
            item = QListWidgetItem(i)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            self.listWidgetOutputDir.addItem(item)

