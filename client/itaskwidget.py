# -*- coding: utf-8 -*-
import os
import sys

#Qt resources.
from PySide2.QtWidgets import*
from PySide2.QtGui import*

import shlex

from parameter.panel import Panel

class ITaskWidget(QWidget):
    def __init__(self,task,parent=None):
        super(ITaskWidget,self).__init__(parent=parent)
        self.task = task

        # self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))

        # self.verticalLayoutCommon = QVBoxLayout(self)
        # self.verticalLayoutCommon.setObjectName("verticalLayoutCommon")
        # self.deadlineCommonWidget = DeadlineCommonWidget(task=self.task)
        # self.verticalLayoutCommon.addWidget(self.deadlineCommonWidget)

    def setToGui(self):
        pass

    def getTask(self):
        return self.task

    def getIcon(self):
        return QIcon(':images/kinoko.png')

    def makeOptionListFromOptionStr(self,optionStr):
        option = shlex.split(optionStr)
        optionTmp = []
        for o in option:
            if ' ' in o:
                o = '\"' + o + "\""
            optionTmp.append(o)
        return optionTmp

class TaskPanel(Panel):

    def __init__(self,task):
        super(TaskPanel, self).__init__(paramSet=task)

    def getTask(self):
        return self.paramSet

    def getIcon(self):
        return QIcon(':images/kinoko.png')

    def makeOptionListFromOptionStr(self, optionStr):
        option = shlex.split(optionStr)
        optionTmp = []
        for o in option:
            if ' ' in o:
                o = '\"' + o + "\""
            optionTmp.append(o)
        return optionTmp
