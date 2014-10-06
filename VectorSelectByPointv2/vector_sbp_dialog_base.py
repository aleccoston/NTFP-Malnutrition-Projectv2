# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'vector_sbp_dialog_base.ui'
#
# Created: Wed Sep  3 00:14:46 2014
#      by: PyQt4 UI code generator 4.11.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_VectorSelectByPointDialogBase(object):
    def setupUi(self, VectorSelectByPointDialogBase):
        VectorSelectByPointDialogBase.setObjectName(_fromUtf8("VectorSelectByPointDialogBase"))
        VectorSelectByPointDialogBase.resize(406, 341)
        self.button_box = QtGui.QDialogButtonBox(VectorSelectByPointDialogBase)
        self.button_box.setGeometry(QtCore.QRect(40, 280, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.button_box.setObjectName(_fromUtf8("button_box"))
        self.txtFeedback = QtGui.QTextBrowser(VectorSelectByPointDialogBase)
        self.txtFeedback.setGeometry(QtCore.QRect(40, 10, 311, 251))
        self.txtFeedback.setObjectName(_fromUtf8("txtFeedback"))
        self.chkActivate = QtGui.QCheckBox(VectorSelectByPointDialogBase)
        self.chkActivate.setGeometry(QtCore.QRect(40, 280, 87, 41))
        self.chkActivate.setObjectName(_fromUtf8("chkActivate"))

        self.retranslateUi(VectorSelectByPointDialogBase)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("accepted()")), VectorSelectByPointDialogBase.accept)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("rejected()")), VectorSelectByPointDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(VectorSelectByPointDialogBase)

    def retranslateUi(self, VectorSelectByPointDialogBase):
        VectorSelectByPointDialogBase.setWindowTitle(_translate("VectorSelectByPointDialogBase", "vector_selectbypoint", None))
        self.chkActivate.setText(_translate("VectorSelectByPointDialogBase", "Activate\n"
"(Check)", None))

