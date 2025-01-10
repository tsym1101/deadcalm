from PySide2.QtWidgets import*
from parameter.core import Parameter
from parameter.core import ParamSet
from parameter.panel import Panel
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    paramSet = ParamSet()
    paramSet.aaa = Parameter('aaa',widget='lineedit')
    paramSet.aaa1 = Parameter('bbb',widget='lineedit')
    paramSet.aaa2 = Parameter(100,widget='spinbox')
    paramSet.aaa3 = Parameter([1,5,100],widget='spinboxarray',min=10,max=30)
    paramSet.aaa4 = Parameter(["1",'5','100'],widget='listwidget')
    panel = Panel(paramSet=paramSet)
    panel.show()
    app.exec_()
