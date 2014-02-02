# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\verifyDeleteDialog.ui'
#
# Created: Fri Jan 31 15:33:01 2014
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_verifyDeleteDialog(object):
    def setupUi(self, verifyDeleteDialog):
        verifyDeleteDialog.setObjectName(_fromUtf8("verifyDeleteDialog"))
        verifyDeleteDialog.setWindowModality(QtCore.Qt.NonModal)
        verifyDeleteDialog.resize(407, 216)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/cross-circle")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        verifyDeleteDialog.setWindowIcon(icon)
        verifyDeleteDialog.setModal(True)
        self.buttonBox = QtGui.QDialogButtonBox(verifyDeleteDialog)
        self.buttonBox.setGeometry(QtCore.QRect(50, 170, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.No|QtGui.QDialogButtonBox.Yes)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayoutWidget = QtGui.QWidget(verifyDeleteDialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(50, 20, 321, 121))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)

        self.retranslateUi(verifyDeleteDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), verifyDeleteDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), verifyDeleteDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(verifyDeleteDialog)

    def retranslateUi(self, verifyDeleteDialog):
        verifyDeleteDialog.setWindowTitle(QtGui.QApplication.translate("verifyDeleteDialog", "Delete Project", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("verifyDeleteDialog", "<html><head/><body><p align=\"center\"><span style=\" font-size:10pt;\">Are you sure you want to </span><span style=\" font-size:10pt; font-weight:600; font-style:italic; color:#ff0000;\">delete</span><span style=\" font-size:10pt;\"> project </span></p><p align=\"center\"><span style=\" font-size:10pt; font-weight:600;\">@project@</span><span style=\" font-size:10pt;\"> ? </span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

import creepy_resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    verifyDeleteDialog = QtGui.QDialog()
    ui = Ui_verifyDeleteDialog()
    ui.setupUi(verifyDeleteDialog)
    verifyDeleteDialog.show()
    sys.exit(app.exec_())

