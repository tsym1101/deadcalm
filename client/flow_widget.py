# -*- coding: utf-8 -*-
#Qt resources.
import gui_resources_rc
import sys
from PySide2.QtWidgets import*
from PySide2.QtGui import*
from PySide2.QtCore import*
from PySide2.QtUiTools import*

from client.taskflowitem import TaskFlowItem
import dutil
from client.jobbase import JobBase

class TaskFlowWidget(QTreeWidget):
    def __init__(self,job,parent=None):
        super(TaskFlowWidget,self).__init__(parent=parent)

        self.job = job

        self.addTopLevelItem(QTreeWidgetItem())
        self.setHeaderHidden(True)
        self.setFont(QFont('Yu Gothic UI', 14))
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setAlternatingRowColors(True)
        # self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred))
        # self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding))
        # self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding))
        # self.setMinimumSize(QSize(300,0))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # self.resizeColumnToContents(0);
        # self.collapseAll()
        # self.expandAll()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            root = self.invisibleRootItem()
            for item in self.selectedItems():
                item.destroy()
                (item.parent() or root).removeChild(item)
            return
        elif event.key() == Qt.Key_D:
            self.resetTaskConnection()
            return

        super(TaskFlowWidget, self).keyPressEvent(event)

    def dropEvent(self,event):
        super(TaskFlowWidget, self).dropEvent(event)
        self.resetTaskConnection()

    def traverse(self,item):
        task = item.getTask()
        for i in range(item.childCount()):
            childItem = item.child(i)
            self.traverse(childItem)
            childTask = childItem.getTask()
            childTask.isolate()
            task.addChild(childTask)




    def resetTaskConnection(self):
        root = self.invisibleRootItem()
        for i in range(root.childCount()):
            childItem = root.child(i)
            self.traverse(childItem)
            task = childItem.getTask()
            task.isolate()
            self.job.addChild(task)

        dutil.logDebug('reset connection.')



