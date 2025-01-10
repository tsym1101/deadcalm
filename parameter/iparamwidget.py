# -*- coding: utf-8 -*-

from PySide2.QtWidgets import*

class IParamWidget(QWidget):
    def __init__(self,parameter,parent=None):
        super(IParamWidget,self).__init__(parent=parent)
        self.parameter = parameter

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.horizontalLayout = QHBoxLayout(self)
        # self.horizontalLayout.setSpacing(0)
        # self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setContentsMargins(3,3,3,3)
        self.setLayout(self.horizontalLayout)

    def addWidget(self,w):
        self.horizontalLayout.addWidget(w)




