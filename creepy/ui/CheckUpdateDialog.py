# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\updateCheckDialog.ui'
#
# Created: Wed Jan 08 19:47:23 2014
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_UpdateAvailableDialog(object):
    def setupUi(self, UpdateAvailableDialog):
        UpdateAvailableDialog.setObjectName(_fromUtf8("UpdateAvailableDialog"))
        UpdateAvailableDialog.resize(594, 300)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/cr/Eye_of_Sauron_by_Blood_Solice.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        UpdateAvailableDialog.setWindowIcon(icon)
        self.buttonBox = QtGui.QDialogButtonBox(UpdateAvailableDialog)
        self.buttonBox.setGeometry(QtCore.QRect(240, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayoutWidget = QtGui.QWidget(UpdateAvailableDialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 571, 221))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.versionsTableWidget = QtGui.QTableWidget(self.verticalLayoutWidget)
        self.versionsTableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.versionsTableWidget.setTabKeyNavigation(False)
        self.versionsTableWidget.setProperty("showDropIndicator", False)
        self.versionsTableWidget.setRowCount(1)
        self.versionsTableWidget.setColumnCount(4)
        self.versionsTableWidget.setObjectName(_fromUtf8("versionsTableWidget"))
        item = QtGui.QTableWidgetItem()
        self.versionsTableWidget.setItem(0, 0, item)
        item = QtGui.QTableWidgetItem()
        self.versionsTableWidget.setItem(0, 1, item)
        item = QtGui.QTableWidgetItem()
        self.versionsTableWidget.setItem(0, 2, item)
        self.versionsTableWidget.horizontalHeader().setStretchLastSection(True)
        self.versionsTableWidget.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.versionsTableWidget)

        self.retranslateUi(UpdateAvailableDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), UpdateAvailableDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), UpdateAvailableDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(UpdateAvailableDialog)

    def retranslateUi(self, UpdateAvailableDialog):
        UpdateAvailableDialog.setWindowTitle(QtGui.QApplication.translate("UpdateAvailableDialog", "Update Check", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("UpdateAvailableDialog", "<html><head/><body><p><span style=\" font-weight:600;\">Results of Update Check</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        __sortingEnabled = self.versionsTableWidget.isSortingEnabled()
        self.versionsTableWidget.setSortingEnabled(False)
        self.versionsTableWidget.setSortingEnabled(__sortingEnabled)

import creepy_resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    UpdateAvailableDialog = QtGui.QDialog()
    ui = Ui_UpdateAvailableDialog()
    ui.setupUi(UpdateAvailableDialog)
    UpdateAvailableDialog.show()
    sys.exit(app.exec_())

