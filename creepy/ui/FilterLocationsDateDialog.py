# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\filterLocationsDateDialog.ui'
#
# Created: Fri Jan 31 15:33:14 2014
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_FilterLocationsDateDialog(object):
    def setupUi(self, FilterLocationsDateDialog):
        FilterLocationsDateDialog.setObjectName(_fromUtf8("FilterLocationsDateDialog"))
        FilterLocationsDateDialog.resize(575, 403)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/calendar")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        FilterLocationsDateDialog.setWindowIcon(icon)
        FilterLocationsDateDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(FilterLocationsDateDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.containerLayout = QtGui.QVBoxLayout()
        self.containerLayout.setObjectName(_fromUtf8("containerLayout"))
        self.titleLabel = QtGui.QLabel(FilterLocationsDateDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.titleLabel.sizePolicy().hasHeightForWidth())
        self.titleLabel.setSizePolicy(sizePolicy)
        self.titleLabel.setObjectName(_fromUtf8("titleLabel"))
        self.containerLayout.addWidget(self.titleLabel)
        self.calendarContainerLayout = QtGui.QHBoxLayout()
        self.calendarContainerLayout.setObjectName(_fromUtf8("calendarContainerLayout"))
        self.startDateContainer = QtGui.QVBoxLayout()
        self.startDateContainer.setObjectName(_fromUtf8("startDateContainer"))
        self.startDateLabel = QtGui.QLabel(FilterLocationsDateDialog)
        self.startDateLabel.setTextFormat(QtCore.Qt.AutoText)
        self.startDateLabel.setObjectName(_fromUtf8("startDateLabel"))
        self.startDateContainer.addWidget(self.startDateLabel)
        self.stardateCalendarWidget = QtGui.QCalendarWidget(FilterLocationsDateDialog)
        self.stardateCalendarWidget.setObjectName(_fromUtf8("stardateCalendarWidget"))
        self.startDateContainer.addWidget(self.stardateCalendarWidget)
        self.calendarContainerLayout.addLayout(self.startDateContainer)
        self.endDateContainer = QtGui.QVBoxLayout()
        self.endDateContainer.setObjectName(_fromUtf8("endDateContainer"))
        self.endDateLabel = QtGui.QLabel(FilterLocationsDateDialog)
        self.endDateLabel.setObjectName(_fromUtf8("endDateLabel"))
        self.endDateContainer.addWidget(self.endDateLabel)
        self.endDateCalendarWidget = QtGui.QCalendarWidget(FilterLocationsDateDialog)
        self.endDateCalendarWidget.setObjectName(_fromUtf8("endDateCalendarWidget"))
        self.endDateContainer.addWidget(self.endDateCalendarWidget)
        self.calendarContainerLayout.addLayout(self.endDateContainer)
        self.containerLayout.addLayout(self.calendarContainerLayout)
        self.timeContainerLayout = QtGui.QHBoxLayout()
        self.timeContainerLayout.setObjectName(_fromUtf8("timeContainerLayout"))
        self.startDateTimeEdit = QtGui.QTimeEdit(FilterLocationsDateDialog)
        self.startDateTimeEdit.setObjectName(_fromUtf8("startDateTimeEdit"))
        self.timeContainerLayout.addWidget(self.startDateTimeEdit)
        self.endDateTimeEdit = QtGui.QTimeEdit(FilterLocationsDateDialog)
        self.endDateTimeEdit.setObjectName(_fromUtf8("endDateTimeEdit"))
        self.timeContainerLayout.addWidget(self.endDateTimeEdit)
        self.containerLayout.addLayout(self.timeContainerLayout)
        self.verticalLayout.addLayout(self.containerLayout)
        self.buttonBox = QtGui.QDialogButtonBox(FilterLocationsDateDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(FilterLocationsDateDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FilterLocationsDateDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FilterLocationsDateDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(FilterLocationsDateDialog)

    def retranslateUi(self, FilterLocationsDateDialog):
        FilterLocationsDateDialog.setWindowTitle(QtGui.QApplication.translate("FilterLocationsDateDialog", "Filter Locations By Date", None, QtGui.QApplication.UnicodeUTF8))
        self.titleLabel.setText(QtGui.QApplication.translate("FilterLocationsDateDialog", "<html><head/><body><p><span style=\" font-size:9pt;\">Select the start and end dates and times</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.startDateLabel.setText(QtGui.QApplication.translate("FilterLocationsDateDialog", "<b>Start Date</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.endDateLabel.setText(QtGui.QApplication.translate("FilterLocationsDateDialog", "<b>End Date</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.startDateTimeEdit.setDisplayFormat(QtGui.QApplication.translate("FilterLocationsDateDialog", "hh:mm:ss AP", None, QtGui.QApplication.UnicodeUTF8))

import creepy_resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    FilterLocationsDateDialog = QtGui.QDialog()
    ui = Ui_FilterLocationsDateDialog()
    ui.setupUi(FilterLocationsDateDialog)
    FilterLocationsDateDialog.show()
    sys.exit(app.exec_())

