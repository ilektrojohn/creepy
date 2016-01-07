# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Development/python/creepy/gui/compareProjectsDialog.ui'
#
# Created: Thu Oct  2 20:31:01 2014
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_compareProjectsDialog(object):
    def setupUi(self, compareProjectsDialog):
        compareProjectsDialog.setObjectName(_fromUtf8("compareProjectsDialog"))
        compareProjectsDialog.resize(928, 403)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/calendar")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        compareProjectsDialog.setWindowIcon(icon)
        compareProjectsDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(compareProjectsDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.containerLayout = QtGui.QVBoxLayout()
        self.containerLayout.setObjectName(_fromUtf8("containerLayout"))
        self.titleLabel = QtGui.QLabel(compareProjectsDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.titleLabel.sizePolicy().hasHeightForWidth())
        self.titleLabel.setSizePolicy(sizePolicy)
        self.titleLabel.setObjectName(_fromUtf8("titleLabel"))
        self.containerLayout.addWidget(self.titleLabel)
        self.projectsSelectionContainerLayout = QtGui.QHBoxLayout()
        self.projectsSelectionContainerLayout.setObjectName(_fromUtf8("projectsSelectionContainerLayout"))
        self.firstProjectContainer = QtGui.QVBoxLayout()
        self.firstProjectContainer.setObjectName(_fromUtf8("firstProjectContainer"))
        self.firstProjectLabel = QtGui.QLabel(compareProjectsDialog)
        self.firstProjectLabel.setTextFormat(QtCore.Qt.AutoText)
        self.firstProjectLabel.setObjectName(_fromUtf8("firstProjectLabel"))
        self.firstProjectContainer.addWidget(self.firstProjectLabel)
        self.firstProjectListWidget = QtGui.QListWidget(compareProjectsDialog)
        self.firstProjectListWidget.setObjectName(_fromUtf8("firstProjectListWidget"))
        self.firstProjectContainer.addWidget(self.firstProjectListWidget)
        self.projectsSelectionContainerLayout.addLayout(self.firstProjectContainer)
        self.secondProjectContainer = QtGui.QVBoxLayout()
        self.secondProjectContainer.setObjectName(_fromUtf8("secondProjectContainer"))
        self.secondProjectLabel = QtGui.QLabel(compareProjectsDialog)
        self.secondProjectLabel.setObjectName(_fromUtf8("secondProjectLabel"))
        self.secondProjectContainer.addWidget(self.secondProjectLabel)
        self.secondProjectListWidget = QtGui.QListWidget(compareProjectsDialog)
        self.secondProjectListWidget.setObjectName(_fromUtf8("secondProjectListWidget"))
        self.secondProjectContainer.addWidget(self.secondProjectListWidget)
        self.projectsSelectionContainerLayout.addLayout(self.secondProjectContainer)
        self.containerLayout.addLayout(self.projectsSelectionContainerLayout)
        self.verticalLayout.addLayout(self.containerLayout)
        self.buttonBox = QtGui.QDialogButtonBox(compareProjectsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(compareProjectsDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), compareProjectsDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), compareProjectsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(compareProjectsDialog)

    def retranslateUi(self, compareProjectsDialog):
        compareProjectsDialog.setWindowTitle(_translate("compareProjectsDialog", "Compare Projects", None))
        self.titleLabel.setText(_translate("compareProjectsDialog", "<html><head/><body><p><span style=\" font-size:9pt;\">Select the two projects you want to compare</span></p></body></html>", None))
        self.firstProjectLabel.setText(_translate("compareProjectsDialog", "<html><head/><body><p><span style=\" font-weight:600;\">Project A</span></p></body></html>", None))
        self.secondProjectLabel.setText(_translate("compareProjectsDialog", "<html><head/><body><p><span style=\" font-weight:600;\">Project B</span></p></body></html>", None))

import creepy_resources_rc
