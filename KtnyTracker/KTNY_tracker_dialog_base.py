# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'KTNY_tracker_dialog_base.ui'
#
# Created: Fri Aug 29 13:41:42 2014
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

class Ui_KtnyTrackerDialogBase(object):
    def setupUi(self, KtnyTrackerDialogBase):
        KtnyTrackerDialogBase.setObjectName(_fromUtf8("KtnyTrackerDialogBase"))
        KtnyTrackerDialogBase.resize(400, 300)
        self.button_box = QtGui.QDialogButtonBox(KtnyTrackerDialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.button_box.setObjectName(_fromUtf8("button_box"))

        self.retranslateUi(KtnyTrackerDialogBase)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("accepted()")), KtnyTrackerDialogBase.accept)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("rejected()")), KtnyTrackerDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(KtnyTrackerDialogBase)

    def retranslateUi(self, KtnyTrackerDialogBase):
        KtnyTrackerDialogBase.setWindowTitle(_translate("KtnyTrackerDialogBase", "KTNY tracker", None))

