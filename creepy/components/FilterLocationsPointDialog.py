#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtGui import QDialog
from PyQt4.QtCore import QObject, pyqtSlot
from ui.FilterLocationsPointDialog import Ui_FilteLocationsPointDialog


class FilterLocationsPointDialog(QDialog):
    """ Loads the Filter Locations by Point Dialog from the ui and shows it """
    def __init__(self, parent=None):
        # Load the UI from the python file
        QDialog.__init__(self, parent)
        self.ui = Ui_FilteLocationsPointDialog()
        self.ui.setupUi(self)
        self.unit = 'km'

    def onUnitChanged(self, index):
        self.unit = index

    class PyObj(QObject):
        def __init__(self):
            QObject.__init__(self)
            self.lat = None
            self.lng = None

        @pyqtSlot(str)
        def setLatLng(self, latlng):
            lat, lng = latlng.replace('(', '').replace(')', '').split(',')
            self.lat = float(lat)
            self.lng = float(lng)
