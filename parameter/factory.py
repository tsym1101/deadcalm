# -*- coding: utf-8 -*-


from PySide2.QtWidgets import*
from PySide2.QtGui import*
from PySide2.QtCore import*
from PySide2.QtUiTools import*

from .core import Parameter
from .core import ParamSet
from .iparamwidget import IParamWidget
import dutil

import sys
import shlex
import re

class LineEdit(IParamWidget):
    def __init__(self,parameter,parent=None):
        super(LineEdit,self).__init__(parameter=parameter,parent=parent)
        self.lineEdit = QLineEdit(parent=self)
        self.addWidget(self.lineEdit)
        self.lineEdit.editingFinished.connect(self.on_lineEditFileName_editingFinished)
        self.setToGui()

    def on_lineEditFileName_editingFinished(self):
        self.parameter.data = self.lineEdit.text()
    def setToGui(self):
        self.lineEdit.setText(self.parameter.data)

class FileWidget(IParamWidget):
    def __init__(self, parameter, parent=None):
        super(FileWidget, self).__init__(parameter=parameter, parent=parent)
        self.lineEdit = QLineEdit(parent=self)
        self.pushButton = QPushButton(parent=self)
        self.pushButton.setText('...')
        self.addWidget(self.lineEdit)
        self.addWidget(self.pushButton)
        self.lineEdit.editingFinished.connect(self.on_lineEditFileName_editingFinished)
        self.pushButton.clicked.connect(self.on_pushButton_clicked)
        self.setToGui()
        self.filter = parameter.kwargs.get('filter')
        if not self.filter:
            self.filter = "* (*.*)"
        self.hint = parameter.kwargs.get('hint')
        if not self.hint:
            self.hint = 'select file'
        self.dir = parameter.kwargs.get('dir')#bool

    def on_lineEditFileName_editingFinished(self):
        self.parameter.data = self.lineEdit.text()
    def setToGui(self):
        self.lineEdit.setText(self.parameter.data)
    def on_pushButton_clicked(self):
        if self.dir:
            dirPath = QFileDialog.getExistingDirectory(self)
            self.parameter.data = dirPath
            self.lineEdit.setText(dirPath)
        else:
            filePath = QFileDialog.getOpenFileName(self, self.hint, filter=self.filter)
            self.parameter.data = filePath[0]
            self.lineEdit.setText(filePath[0])

class SpinBox(IParamWidget):
    def __init__(self,parameter,parent=None):
        super(SpinBox,self).__init__(parameter=parameter,parent=parent)
        self.spinBox = QSpinBox(parent=self)
        self.addWidget(self.spinBox)
        self.setToGui()
        self.spinBox.valueChanged[int].connect(self.on_spinBox_valueChanged)

        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
    def on_spinBox_valueChanged(self, i):
        self.parameter.data = i
    def setToGui(self):

        min = self.parameter.kwargs.get('min')
        max = self.parameter.kwargs.get('max')
        step = self.parameter.kwargs.get('step')
        if min is None:
            min = 0
        if max is None:
            max = 1000000
        if step is None:
            step = 1
        self.spinBox.setMinimum(min)
        self.spinBox.setMaximum(max)
        self.spinBox.setSingleStep(step)

        self.spinBox.setValue(self.parameter.data)

class DoubleSpinBox(IParamWidget):
    def __init__(self,parameter,parent=None):
        super(DoubleSpinBox,self).__init__(parameter=parameter,parent=parent)
        self.spinBox = QDoubleSpinBox(parent=self)
        self.addWidget(self.spinBox)
        self.setToGui()
        self.spinBox.valueChanged[float].connect(self.on_spinBox_valueChanged)

    def on_spinBox_valueChanged(self, i):
        self.parameter.data = i
        print(self.parameter.data)
    def setToGui(self):

        min = self.parameter.kwargs.get('min')
        max = self.parameter.kwargs.get('max')
        step = self.parameter.kwargs.get('step')
        decimals = self.parameter.kwargs.get('decimals')
        if min is None:
            min = 0
        if max is None:
            max = 1000000
        if step is None:
            step = 1
        if decimals is None:
            decimals = 3
        self.spinBox.setMinimum(min)
        self.spinBox.setMaximum(max)
        self.spinBox.setSingleStep(step)
        self.spinBox.setDecimals(decimals)

        self.spinBox.setValue(self.parameter.data)

class ComboBox(IParamWidget):
    def __init__(self,parameter,parent=None):
        super(ComboBox,self).__init__(parameter=parameter,parent=parent)
        self.comboBox = QComboBox(parent=self)
        self.addWidget(self.comboBox)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.comboBox.activated[str].connect(self.on_comboBox_activated)
        self.setToGui()
    def on_comboBox_activated(self,s):
        self.parameter.data =s
    def setToGui(self):
        items = self.parameter.kwargs.get('items')
        if items is not None:
            self.comboBox.addItems(items)
        if not self.parameter.data:
            self.comboBox.setCurrentIndex(-1)
        else:
            itemTexts = [self.comboBox.itemText(i) for i in range(self.comboBox.count()) ]
            if self.parameter.data not in itemTexts:
                self.comboBox.addItem(self.parameter.data)
            self.comboBox.setCurrentText(self.parameter.data)

class CheckBox(IParamWidget):
    def __init__(self,parameter,parent=None):
        super(CheckBox,self).__init__(parameter=parameter,parent=parent)
        self.checkBox = QCheckBox(parent=self)
        self.addWidget(self.checkBox)
        self.checkBox.clicked[bool].connect(self.on_checkBox_clicked)
        self.setToGui()

    def on_checkBox_clicked(self, b):
        self.parameter.data = b
    def setToGui(self):
        self.checkBox.setChecked(self.parameter.data)

class OptionEdit(IParamWidget):
    def __init__(self,parameter,parent=None):
        super(OptionEdit,self).__init__(parameter=parameter,parent=parent)
        self.lineEdit = QLineEdit(parent=self)
        self.addWidget(self.lineEdit)
        self.lineEdit.editingFinished.connect(self.on_OptionEdit_editingFinished)
        self.setToGui()

    def on_OptionEdit_editingFinished(self):
        self.parameter.data = self.makeOptionListFromOptionStr(self.lineEdit.text())
        dutil.logDebug('option {}'.format(self.parameter.data))

    def setToGui(self):

        dutil.logDebug('option {}'.format(self.parameter.data))
        dutil.logDebug('option type  {}'.format(type(self.parameter.data)))
        dutil.logDebug('option len  {}'.format(str(len(self.parameter.data))))

        if not self.parameter.data:
            return
        elif type([]) == type(self.parameter.data) and len(self.parameter.data) == 0:
            return


        value = " ".join(self.parameter.data)
        if value:
            self.lineEdit.setText(value)
        # else:
        #     dutil.logWarn('empty option {}'.format(self.parameter.name))

    def makeOptionListFromOptionStr(self, optionStr):
        option = shlex.split(optionStr)
        optionTmp = []
        for o in option:
            if ' ' in o:
                o = '\"' + o + "\""
            optionTmp.append(o)
        return optionTmp

class SpinBoxSlot:
    def __init__(self,parameter,index):
        self.parameter = parameter
        self.index = index
    def callback(self,i):
        self.parameter.data[self.index] = i

class SpinBoxArray(IParamWidget):
    def __init__(self,parameter,parent=None):
        super(SpinBoxArray,self).__init__(parameter=parameter,parent=parent)

        self.spinBoxes = []
        self.slots = []
        for i in range(len(self.parameter.data)):
            spinBox = QSpinBox(parent=self)
            self.addWidget(spinBox)
            self.spinBoxes.append(spinBox)
            slot = SpinBoxSlot(self.parameter,i)
            spinBox.valueChanged[int].connect(slot.callback)
            self.slots.append(slot)

        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.setToGui()

    def on_spinBox_valueChanged(self, i):
        self.parameter.data = i
    def setToGui(self):
        min = self.parameter.kwargs.get('min')
        max = self.parameter.kwargs.get('max')
        step = self.parameter.kwargs.get('step')
        if min is None:
            min = 0
        if max is None:
            max = 1000000
        if step is None:
            step = 1
        i = 0
        for sb in self.spinBoxes:
            sb.setMinimum(min)
            sb.setMaximum(max)
            sb.setSingleStep(step)
            sb.setValue(self.parameter.data[i])
            i += 1

class ListWidget(IParamWidget):
    def __init__(self,parameter,parent=None):
        super(ListWidget,self).__init__(parameter=parameter,parent=parent)
        self.listWidget = QListWidget(self)
        self.listWidget.setAlternatingRowColors(True)
        self.addWidget(self.listWidget)

        self.verticalLayout_2 = QVBoxLayout()
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.pushButtonAdd = QPushButton('add',self)
        self.verticalLayout_2.addWidget(self.pushButtonAdd)
        self.pushButtonDelete = QPushButton('delete',self)
        self.verticalLayout_2.addWidget(self.pushButtonDelete)

        self.horizontalLayout.addLayout(self.verticalLayout_2)

        # QMetaObject.connectSlotsByName(self)
        self.listWidget.itemChanged.connect(self.on_listWidgetEnv_itemChanged)
        self.pushButtonAdd.pressed.connect(self.on_pushButtonAdd_pressed)
        self.pushButtonDelete.pressed.connect(self.on_pushButtonDelete_pressed)

        self.itemText = self.parameter.kwargs.get('item_text')
        if self.itemText is None:
            self.itemText = '***'

        self.setToGui()

    def setToGui(self):
        self.listWidget.addItems(self.parameter.data)

    def updateData(self):
        self.parameter.data = []
        for i in range(self.listWidget.count()):
            self.parameter.data.append(self.listWidget.item(i).text())

    def on_listWidgetEnv_itemChanged(self):
        self.updateData()

    def on_pushButtonAdd_pressed(self):
        item = QListWidgetItem(self.itemText)
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.listWidget.addItem(item)
        self.updateData()

    def on_pushButtonDelete_pressed(self):
        item = self.listWidget.currentItem()
        self.listWidget.takeItem(self.listWidget.row(item))
        self.updateData()

class PushButton(IParamWidget):

    def __init__(self,parameter,parent=None):
        super(PushButton,self).__init__(parameter=parameter,parent=parent)
        self.pushButton = QPushButton(parent=self)
        self.pushButton.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.MinimumExpanding)
        # self.pushButton.setLayoutDirection(Qt.RightToLeft)
        self.addWidget(self.pushButton)

        name = parameter.alias if self.parameter.alias else self.parameter.name
        text = re.sub(r"([A-Z])", r" \1", name).split()  # 大文字でリストに分割
        text = ' '.join(text).lower()
        self.pushButton.setText(text)
        #
        # self.pushButton.setIcon(QIcon(':images/oneup.png'))
        # self.pushButton.setIconSize(QSize(20,20))

        spacer = self.parameter.kwargs.get('spacer')
        if (spacer is None) or ((spacer is not None) and spacer):
            spacerItem = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
            self.horizontalLayout.addItem(spacerItem)

        ss = self.parameter.kwargs.get('stylesheet')
        if ss is not None:
            self.pushButton.setStyleSheet(ss)

        self.pushButton.pressed.connect(self.on_pushButton_pressed)

    def on_pushButton_pressed(self):
        self.parameter.data() #data is callback

param_widgets = {
    'lineedit':{'class':LineEdit},
    'file':{'class':FileWidget},
    'spinbox':{'class':SpinBox},
    'doublespinbox':{'class':DoubleSpinBox},
    'combobox':{'class':ComboBox},
    'checkbox':{'class':CheckBox},
    'option':{'class':OptionEdit},
    'spinboxarray':{'class':SpinBoxArray},
    'listwidget':{'class':ListWidget},
    'pushbutton':{'class':PushButton,'with_label':False}
}


