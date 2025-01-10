# -*- coding: utf-8 -*-

from PySide2.QtWidgets import*
from PySide2.QtCore import*
from parameter.core import Parameter
from parameter.core import ParamSet
import sys
from parameter import factory
import re

class Panel(QWidget):
    param_widgets = factory.param_widgets #param widgetを追加する場合は、これに追加
    @staticmethod
    def generateUi(parameter):
        return Panel.param_widgets[parameter.widget]['class'](parameter)
    @staticmethod
    def withLabel(parameter):
        withLabel = Panel.param_widgets[parameter.widget].get('with_label')
        if withLabel is not None:
            return withLabel
        else:
            return True

    def __init__(self,paramSet,parent=None):
        super(Panel, self).__init__(parent=parent)

        self.paramSet = paramSet

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.verticalLayout)

        self.layouts = {}
        for param in self.paramSet.params():
            if param.visible:
                name = param.alias if param.alias else param.name

                text = re.sub(r"([A-Z])", r" \1", name).split()  # 大文字でリストに分割
                if text[0] == 'd': #deadlineメンバ変数プリフィックス削除
                    text.pop(0)
                text = ' '.join(text).rjust(30).lower()  # 字埋めして小文字に

                label = None
                if Panel.withLabel(param):
                    label = QLabel(text,parent=self)
                    sizePolicy = QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
                    sizePolicy.setHorizontalStretch(0)
                    sizePolicy.setVerticalStretch(0)
                    sizePolicy.setHeightForWidth(label.sizePolicy().hasHeightForWidth())
                    label.setSizePolicy(sizePolicy)
                widget = Panel.generateUi(param)
                widget.setParent(self)
                widget.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)

                layout = self.layouts.get(param.category)
                if not layout:
                    layout = QFormLayout()
                    layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
                    layout.setLabelAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
                    layout.setSpacing(0)
                    layout.setMargin(0)
                    layout.setContentsMargins(0, 0, 0, 0)
                    self.layouts[param.category] = layout

                    if not param.category == 'default':
                        self.label = QLabel(param.category,self)
                        self.label.setStyleSheet("QWidget{\n"
                                                 "color: white;\n"
                                                 "background-color: rgb(0, 0, 0);\n"
                                                 "}")
                        self.label.setAlignment(Qt.AlignCenter)
                        self.label.setMargin(0)
                        self.verticalLayout.addWidget(self.label)

                    self.verticalLayout.addLayout(layout)


                layout.addRow(label,widget)



if __name__ == '__main__':
    app = QApplication(sys.argv)

    paramSet = ParamSet()
    paramSet.titleaaaaaaaaaaaaaaa = Parameter('hogaaaaaaaaaaaaaaae')

    panel = Panel(paramSet=paramSet)    # l.a = Parameter('aaa')
    panel.show()

    app.exec_()
