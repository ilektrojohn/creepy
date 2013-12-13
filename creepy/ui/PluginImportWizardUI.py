# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\ioannis\workspace-python\creepy\gui\pluginImportWizard.ui'
#
# Created: Thu Dec 12 20:21:27 2013
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_pluginImportWizard(object):
    def setupUi(self, pluginImportWizard):
        pluginImportWizard.setObjectName(_fromUtf8("pluginImportWizard"))
        pluginImportWizard.resize(686, 527)
        pluginImportWizard.setWizardStyle(QtGui.QWizard.ClassicStyle)
        self.pluginImportWizardPage1 = QtGui.QWizardPage()
        self.pluginImportWizardPage1.setObjectName(_fromUtf8("pluginImportWizardPage1"))
        self.verticalLayoutWidget = QtGui.QWidget(self.pluginImportWizardPage1)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 641, 351))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label1 = QtGui.QLabel(self.verticalLayoutWidget)
        self.label1.setTextFormat(QtCore.Qt.RichText)
        self.label1.setAlignment(QtCore.Qt.AlignCenter)
        self.label1.setObjectName(_fromUtf8("label1"))
        self.verticalLayout.addWidget(self.label1)
        pluginImportWizard.addPage(self.pluginImportWizardPage1)
        self.pluginImportWizardPage2 = QtGui.QWizardPage()
        self.pluginImportWizardPage2.setObjectName(_fromUtf8("pluginImportWizardPage2"))
        self.verticalLayoutWidget_2 = QtGui.QWidget(self.pluginImportWizardPage2)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(10, 10, 641, 391))
        self.verticalLayoutWidget_2.setObjectName(_fromUtf8("verticalLayoutWidget_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lineEditFolderName = QtGui.QLineEdit(self.verticalLayoutWidget_2)
        self.lineEditFolderName.setReadOnly(True)
        self.lineEditFolderName.setObjectName(_fromUtf8("lineEditFolderName"))
        self.horizontalLayout.addWidget(self.lineEditFolderName)
        self.btnOpenFileDialog = QtGui.QPushButton(self.verticalLayoutWidget_2)
        self.btnOpenFileDialog.setObjectName(_fromUtf8("btnOpenFileDialog"))
        self.horizontalLayout.addWidget(self.btnOpenFileDialog)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem)
        self.tableViewPossiblePlugins = QtGui.QTableView(self.verticalLayoutWidget_2)
        self.tableViewPossiblePlugins.setSortingEnabled(True)
        self.tableViewPossiblePlugins.setObjectName(_fromUtf8("tableViewPossiblePlugins"))
        self.tableViewPossiblePlugins.verticalHeader().setSortIndicatorShown(True)
        self.tableViewPossiblePlugins.verticalHeader().setStretchLastSection(True)
        self.verticalLayout_2.addWidget(self.tableViewPossiblePlugins)
        pluginImportWizard.addPage(self.pluginImportWizardPage2)

        self.retranslateUi(pluginImportWizard)
        QtCore.QMetaObject.connectSlotsByName(pluginImportWizard)

    def retranslateUi(self, pluginImportWizard):
        pluginImportWizard.setWindowTitle(QtGui.QApplication.translate("pluginImportWizard", "Wizard", None, QtGui.QApplication.UnicodeUTF8))
        self.pluginImportWizardPage1.setTitle(QtGui.QApplication.translate("pluginImportWizard", "Plugin Import Wizard", None, QtGui.QApplication.UnicodeUTF8))
        self.pluginImportWizardPage1.setSubTitle(QtGui.QApplication.translate("pluginImportWizard", "This wizard will help you import new plugins for Creepy", None, QtGui.QApplication.UnicodeUTF8))
        self.label1.setText(QtGui.QApplication.translate("pluginImportWizard", "Click Next to start !", None, QtGui.QApplication.UnicodeUTF8))
        self.pluginImportWizardPage2.setTitle(QtGui.QApplication.translate("pluginImportWizard", "Plugin Import Wizard", None, QtGui.QApplication.UnicodeUTF8))
        self.pluginImportWizardPage2.setSubTitle(QtGui.QApplication.translate("pluginImportWizard", "Indicate the source folder and select the plugin(s) to be imported", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditFolderName.setPlaceholderText(QtGui.QApplication.translate("pluginImportWizard", "Click on the Open button to select the folder that contains your plugins", None, QtGui.QApplication.UnicodeUTF8))
        self.btnOpenFileDialog.setText(QtGui.QApplication.translate("pluginImportWizard", "Open...", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    pluginImportWizard = QtGui.QWizard()
    ui = Ui_pluginImportWizard()
    ui.setupUi(pluginImportWizard)
    pluginImportWizard.show()
    sys.exit(app.exec_())

