# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\pluginConfigCheckDialog.ui'
#
# Created: Fri Jan 31 15:31:13 2014
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_checkPluginConfigurationDialog(object):
    def setupUi(self, checkPluginConfigurationDialog):
        checkPluginConfigurationDialog.setObjectName(_fromUtf8("checkPluginConfigurationDialog"))
        checkPluginConfigurationDialog.resize(378, 222)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(checkPluginConfigurationDialog.sizePolicy().hasHeightForWidth())
        checkPluginConfigurationDialog.setSizePolicy(sizePolicy)
        checkPluginConfigurationDialog.setMinimumSize(QtCore.QSize(378, 222))
        checkPluginConfigurationDialog.setMaximumSize(QtCore.QSize(378, 222))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/creepy")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        checkPluginConfigurationDialog.setWindowIcon(icon)
        checkPluginConfigurationDialog.setModal(True)
        self.checkPluginConfigurationButtonBox = QtGui.QDialogButtonBox(checkPluginConfigurationDialog)
        self.checkPluginConfigurationButtonBox.setGeometry(QtCore.QRect(30, 176, 341, 32))
        self.checkPluginConfigurationButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.checkPluginConfigurationButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.checkPluginConfigurationButtonBox.setObjectName(_fromUtf8("checkPluginConfigurationButtonBox"))
        self.horizontalLayoutWidget = QtGui.QWidget(checkPluginConfigurationDialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 40, 351, 121))
        self.horizontalLayoutWidget.setObjectName(_fromUtf8("horizontalLayoutWidget"))
        self.checkPluginConfigurationHorizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.checkPluginConfigurationHorizontalLayout.setMargin(0)
        self.checkPluginConfigurationHorizontalLayout.setObjectName(_fromUtf8("checkPluginConfigurationHorizontalLayout"))
        self.checkPluginConfigurationResultLabel = QtGui.QLabel(self.horizontalLayoutWidget)
        self.checkPluginConfigurationResultLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.checkPluginConfigurationResultLabel.setWordWrap(True)
        self.checkPluginConfigurationResultLabel.setObjectName(_fromUtf8("checkPluginConfigurationResultLabel"))
        self.checkPluginConfigurationHorizontalLayout.addWidget(self.checkPluginConfigurationResultLabel)

        self.retranslateUi(checkPluginConfigurationDialog)
        QtCore.QObject.connect(self.checkPluginConfigurationButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), checkPluginConfigurationDialog.accept)
        QtCore.QObject.connect(self.checkPluginConfigurationButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), checkPluginConfigurationDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(checkPluginConfigurationDialog)

    def retranslateUi(self, checkPluginConfigurationDialog):
        checkPluginConfigurationDialog.setWindowTitle(QtGui.QApplication.translate("checkPluginConfigurationDialog", "Plugin Configuration Test", None, QtGui.QApplication.UnicodeUTF8))
        self.checkPluginConfigurationResultLabel.setText(QtGui.QApplication.translate("checkPluginConfigurationDialog", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))

import creepy_resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    checkPluginConfigurationDialog = QtGui.QDialog()
    ui = Ui_checkPluginConfigurationDialog()
    ui.setupUi(checkPluginConfigurationDialog)
    checkPluginConfigurationDialog.show()
    sys.exit(app.exec_())

