# -*- coding: utf-8 -*-
#Qt resources.
import gui_resources_rc
import sys
from PySide2.QtWidgets import*
from PySide2.QtGui import*
from PySide2.QtCore import*
from PySide2.QtUiTools import*

from ui_RenderSummaryWidget import *

class RenderSummaryWidget(QWidget, Ui_RenderSummaryWidget):
    def __init__(self,parent=None):
        super(RenderSummaryWidget, self).__init__(parent=parent)
        self.setupUi(self)

if __name__ == '__main__':
    app = QApplication(sys.argv)  # アプリケーションインスタンス
    w = RenderSummaryWidget()
    w.show()

    app.exec_()