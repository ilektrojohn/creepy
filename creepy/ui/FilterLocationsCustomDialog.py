# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Development/python/creepy/gui/filterLocationsCustomDialog.ui'
#
# Created: Wed Oct 15 19:48:10 2014
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

class Ui_FilterLocationsCustomDialog(object):
    def setupUi(self, FilterLocationsCustomDialog):
        FilterLocationsCustomDialog.setObjectName(_fromUtf8("FilterLocationsCustomDialog"))
        FilterLocationsCustomDialog.resize(1202, 403)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/calendar-day.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        FilterLocationsCustomDialog.setWindowIcon(icon)
        FilterLocationsCustomDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(FilterLocationsCustomDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.containerLayout = QtGui.QVBoxLayout()
        self.containerLayout.setObjectName(_fromUtf8("containerLayout"))
        self.titleLabel = QtGui.QLabel(FilterLocationsCustomDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.titleLabel.sizePolicy().hasHeightForWidth())
        self.titleLabel.setSizePolicy(sizePolicy)
        self.titleLabel.setObjectName(_fromUtf8("titleLabel"))
        self.containerLayout.addWidget(self.titleLabel)
        self.fieldsContainerLayout = QtGui.QHBoxLayout()
        self.fieldsContainerLayout.setObjectName(_fromUtf8("fieldsContainerLayout"))
        self.hoursOfDayContainer = QtGui.QVBoxLayout()
        self.hoursOfDayContainer.setObjectName(_fromUtf8("hoursOfDayContainer"))
        self.hoursOfDayLabel = QtGui.QLabel(FilterLocationsCustomDialog)
        self.hoursOfDayLabel.setObjectName(_fromUtf8("hoursOfDayLabel"))
        self.hoursOfDayContainer.addWidget(self.hoursOfDayLabel)
        self.hoursOfDayListWidget = QtGui.QListWidget(FilterLocationsCustomDialog)
        self.hoursOfDayListWidget.setObjectName(_fromUtf8("hoursOfDayListWidget"))
        self.hoursOfDayContainer.addWidget(self.hoursOfDayListWidget)
        self.fieldsContainerLayout.addLayout(self.hoursOfDayContainer)
        self.daysOfWeekContainer = QtGui.QVBoxLayout()
        self.daysOfWeekContainer.setObjectName(_fromUtf8("daysOfWeekContainer"))
        self.daysOfWeekLayout = QtGui.QVBoxLayout()
        self.daysOfWeekLayout.setObjectName(_fromUtf8("daysOfWeekLayout"))
        self.daysOfWeekLabel = QtGui.QLabel(FilterLocationsCustomDialog)
        self.daysOfWeekLabel.setObjectName(_fromUtf8("daysOfWeekLabel"))
        self.daysOfWeekLayout.addWidget(self.daysOfWeekLabel)
        self.daysOfWeekListWidget = QtGui.QListWidget(FilterLocationsCustomDialog)
        self.daysOfWeekListWidget.setObjectName(_fromUtf8("daysOfWeekListWidget"))
        self.daysOfWeekLayout.addWidget(self.daysOfWeekListWidget)
        self.daysOfWeekContainer.addLayout(self.daysOfWeekLayout)
        self.fieldsContainerLayout.addLayout(self.daysOfWeekContainer)
        self.monthsOfYearContainer = QtGui.QVBoxLayout()
        self.monthsOfYearContainer.setObjectName(_fromUtf8("monthsOfYearContainer"))
        self.monthsOfYearLayout = QtGui.QVBoxLayout()
        self.monthsOfYearLayout.setObjectName(_fromUtf8("monthsOfYearLayout"))
        self.monthsOfYearLabel = QtGui.QLabel(FilterLocationsCustomDialog)
        self.monthsOfYearLabel.setTextFormat(QtCore.Qt.AutoText)
        self.monthsOfYearLabel.setObjectName(_fromUtf8("monthsOfYearLabel"))
        self.monthsOfYearLayout.addWidget(self.monthsOfYearLabel)
        self.monthsOfYearListWidget = QtGui.QListWidget(FilterLocationsCustomDialog)
        self.monthsOfYearListWidget.setObjectName(_fromUtf8("monthsOfYearListWidget"))
        self.monthsOfYearLayout.addWidget(self.monthsOfYearListWidget)
        self.monthsOfYearContainer.addLayout(self.monthsOfYearLayout)
        self.fieldsContainerLayout.addLayout(self.monthsOfYearContainer)
        self.containerLayout.addLayout(self.fieldsContainerLayout)
        self.verticalLayout.addLayout(self.containerLayout)
        self.buttonBox = QtGui.QDialogButtonBox(FilterLocationsCustomDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(FilterLocationsCustomDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FilterLocationsCustomDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FilterLocationsCustomDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(FilterLocationsCustomDialog)

    def retranslateUi(self, FilterLocationsCustomDialog):
        FilterLocationsCustomDialog.setWindowTitle(_translate("FilterLocationsCustomDialog", "Filter Locations By Date", None))
        self.titleLabel.setText(_translate("FilterLocationsCustomDialog", "<html><head/><body><p><span style=\" font-size:9pt;\">Select the custom filtering options</span></p></body></html>", None))
        self.hoursOfDayLabel.setText(_translate("FilterLocationsCustomDialog", "<html><head/><body><p><span style=\" font-weight:600;\">Hours in the day</span></p></body></html>", None))
        self.daysOfWeekLabel.setText(_translate("FilterLocationsCustomDialog", "<html><head/><body><p><span style=\" font-weight:600;\">Days of the week</span></p></body></html>", None))
        self.monthsOfYearLabel.setText(_translate("FilterLocationsCustomDialog", "<html><head/><body><p><span style=\" font-weight:600;\">Months of the year</span></p></body></html>", None))

import creepy_resources_rc
