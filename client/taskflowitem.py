# -*- coding: utf-8 -*-
#Qt resources.
import gui_resources_rc

from PySide2.QtWidgets import*
from PySide2.QtGui import*
from PySide2.QtCore import*
from PySide2.QtUiTools import*
from client.taskfactory import getIcon

class TaskFlowItem(QTreeWidgetItem):
    def __init__(self,taskWidget,parent=None):
        super(TaskFlowItem, self).__init__(parent=parent)

        self.taskWidget = taskWidget
        self.setText(0,taskWidget.getTask().title)
        self.setIcon(0,getIcon(taskWidget.getTask().taskType))
        self.setFlags(self.flags() | Qt.ItemIsEditable)

    def __del__(self):
        pass

    #keyでdelete時のみ使用
    def destroy(self):
        task = self.getTask()
        task.destory()
        del task
        del self.taskWidget

    def getTask(self):
        return self.taskWidget.getTask()

    def getWidget(self):
        return self.taskWidget


