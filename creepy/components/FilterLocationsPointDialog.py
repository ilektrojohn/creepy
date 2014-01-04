#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtGui import QDialog
from PyQt4.QtCore import QObject, pyqtSlot
from ui.FilterLocationsPointDialog import Ui_FilteLocationsPointDialog
class FilterLocationsPointDialog(QDialog):
    def __init__(self, parent=None):
        # Load the UI from the python file
        QDialog.__init__(self, parent)
        self.ui = Ui_FilteLocationsPointDialog()
        self.ui.setupUi(self)
        self.unit = 'km'
    
    def onUnitChanged(self, index):
        self.unit = index 

    class pyObj(QObject):
        def __init__(self, parent=None):
            QObject.__init__(self)
            self.selectedLat = None
            self.selectedLng = None
        @pyqtSlot(str)     
        def setLatLng(self, latlng):
            lat, lng = latlng.replace('(', '').replace(')', '').split(',')
            self.lat = float(lat)
            self.lng = float(lng)
            