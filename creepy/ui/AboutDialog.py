# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\aboutDialog.ui'
#
# Created: Sat Dec 14 23:25:37 2013
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_aboutDialog(object):
    def setupUi(self, aboutDialog):
        aboutDialog.setObjectName(_fromUtf8("aboutDialog"))
        aboutDialog.resize(394, 338)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/cr/creepy32.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        aboutDialog.setWindowIcon(icon)
        aboutDialog.setModal(False)
        self.buttonBox = QtGui.QDialogButtonBox(aboutDialog)
        self.buttonBox.setGeometry(QtCore.QRect(20, 290, 361, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayoutWidget = QtGui.QWidget(aboutDialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 10, 361, 281))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.verticalLayoutWidget)
        self.label.setTextFormat(QtCore.Qt.RichText)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)

        self.retranslateUi(aboutDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), aboutDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), aboutDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(aboutDialog)

    def retranslateUi(self, aboutDialog):
        aboutDialog.setWindowTitle(QtGui.QApplication.translate("aboutDialog", "About", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("aboutDialog", "<html><head/><body><p align=\"center\"><img src=\":/cr/creepy32.png\"/></p><p><br/></p><p align=\"center\"><span style=\" font-size:9pt;\">Creepy is a geolocation OSINT tool. </span></p><p><br/></p><p><span style=\" font-weight:600;\">Author</span> : Ioannis Kakavas &lt; jkakavas@gmail.com &gt;</p><p><span style=\" font-weight:600;\">Website</span>: www.geocreepy.net</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

import creepy_resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    aboutDialog = QtGui.QDialog()
    ui = Ui_aboutDialog()
    ui.setupUi(aboutDialog)
    aboutDialog.show()
    sys.exit(app.exec_())

