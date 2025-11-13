# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/pluginRatesCheckDialog.ui'
#
# Created: Mon Oct  5 21:20:08 2015
#      by: PyQt4 UI code generator 4.11.3
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

class Ui_checkPluginRatesDialog(object):
    def setupUi(self, checkPluginRatesDialog):
        checkPluginRatesDialog.setObjectName(_fromUtf8("checkPluginRatesDialog"))
        checkPluginRatesDialog.resize(963, 300)
        self.checkPluginRatesButtonBox = QtGui.QDialogButtonBox(checkPluginRatesDialog)
        self.checkPluginRatesButtonBox.setGeometry(QtCore.QRect(600, 250, 341, 32))
        self.checkPluginRatesButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.checkPluginRatesButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.checkPluginRatesButtonBox.setObjectName(_fromUtf8("checkPluginRatesButtonBox"))
        self.horizontalLayoutWidget = QtGui.QWidget(checkPluginRatesDialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 10, 951, 231))
        self.horizontalLayoutWidget.setObjectName(_fromUtf8("horizontalLayoutWidget"))
        self.checkPluginRatesHorizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.checkPluginRatesHorizontalLayout.setMargin(0)
        self.checkPluginRatesHorizontalLayout.setObjectName(_fromUtf8("checkPluginRatesHorizontalLayout"))
        self.checkPluginRatesLabel = QtGui.QLabel(self.horizontalLayoutWidget)
        self.checkPluginRatesLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.checkPluginRatesLabel.setObjectName(_fromUtf8("checkPluginRatesLabel"))
        self.checkPluginRatesHorizontalLayout.addWidget(self.checkPluginRatesLabel)

        self.retranslateUi(checkPluginRatesDialog)
        QtCore.QObject.connect(self.checkPluginRatesButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), checkPluginRatesDialog.accept)
        QtCore.QObject.connect(self.checkPluginRatesButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), checkPluginRatesDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(checkPluginRatesDialog)

    def retranslateUi(self, checkPluginRatesDialog):
        checkPluginRatesDialog.setWindowTitle(_translate("checkPluginRatesDialog", "Plugin API Rate Limit Information", None))
        self.checkPluginRatesLabel.setText(_translate("checkPluginRatesDialog", "TextLabel", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    checkPluginRatesDialog = QtGui.QDialog()
    ui = Ui_checkPluginRatesDialog()
    ui.setupUi(checkPluginRatesDialog)
    checkPluginRatesDialog.show()
    sys.exit(app.exec_())

