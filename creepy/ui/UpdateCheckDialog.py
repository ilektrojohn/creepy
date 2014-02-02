# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\updateCheckDialog.ui'
#
# Created: Fri Jan 31 15:29:49 2014
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_UpdateCheckDialog(object):
    def setupUi(self, UpdateCheckDialog):
        UpdateCheckDialog.setObjectName(_fromUtf8("UpdateCheckDialog"))
        UpdateCheckDialog.resize(473, 300)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/creepy")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        UpdateCheckDialog.setWindowIcon(icon)
        self.buttonBox = QtGui.QDialogButtonBox(UpdateCheckDialog)
        self.buttonBox.setGeometry(QtCore.QRect(110, 250, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayoutWidget = QtGui.QWidget(UpdateCheckDialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 451, 221))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.verticalLayoutWidget)
        self.label.setOpenExternalLinks(False)
        self.label.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.versionsTableWidget = QtGui.QTableWidget(self.verticalLayoutWidget)
        self.versionsTableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.versionsTableWidget.setTabKeyNavigation(False)
        self.versionsTableWidget.setProperty("showDropIndicator", False)
        self.versionsTableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.versionsTableWidget.setTextElideMode(QtCore.Qt.ElideNone)
        self.versionsTableWidget.setRowCount(1)
        self.versionsTableWidget.setColumnCount(5)
        self.versionsTableWidget.setObjectName(_fromUtf8("versionsTableWidget"))
        item = QtGui.QTableWidgetItem()
        self.versionsTableWidget.setItem(0, 0, item)
        item = QtGui.QTableWidgetItem()
        self.versionsTableWidget.setItem(0, 1, item)
        item = QtGui.QTableWidgetItem()
        self.versionsTableWidget.setItem(0, 2, item)
        item = QtGui.QTableWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        self.versionsTableWidget.setItem(0, 3, item)
        self.versionsTableWidget.horizontalHeader().setCascadingSectionResizes(True)
        self.versionsTableWidget.horizontalHeader().setDefaultSectionSize(80)
        self.versionsTableWidget.horizontalHeader().setStretchLastSection(True)
        self.versionsTableWidget.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.versionsTableWidget)
        self.dlNewVersionLabel = QtGui.QLabel(self.verticalLayoutWidget)
        self.dlNewVersionLabel.setText(_fromUtf8(""))
        self.dlNewVersionLabel.setOpenExternalLinks(True)
        self.dlNewVersionLabel.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse)
        self.dlNewVersionLabel.setObjectName(_fromUtf8("dlNewVersionLabel"))
        self.verticalLayout.addWidget(self.dlNewVersionLabel)

        self.retranslateUi(UpdateCheckDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), UpdateCheckDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), UpdateCheckDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(UpdateCheckDialog)

    def retranslateUi(self, UpdateCheckDialog):
        UpdateCheckDialog.setWindowTitle(QtGui.QApplication.translate("UpdateCheckDialog", "Update Check", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("UpdateCheckDialog", "<html><head/><body><p><span style=\" font-weight:600;\">Results of Update Check</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        __sortingEnabled = self.versionsTableWidget.isSortingEnabled()
        self.versionsTableWidget.setSortingEnabled(False)
        self.versionsTableWidget.setSortingEnabled(__sortingEnabled)

import creepy_resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    UpdateCheckDialog = QtGui.QDialog()
    ui = Ui_UpdateCheckDialog()
    ui.setupUi(UpdateCheckDialog)
    UpdateCheckDialog.show()
    sys.exit(app.exec_())

