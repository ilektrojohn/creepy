#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtGui import QDialog
from ui.FilterLocationsCustomDialog import Ui_FilterLocationsCustomDialog


class FilterLocationsCustomDialog(QDialog):
    """ Loads the Filter Locations Custom Dialog from the ui and shows it """
    def __init__(self, parent=None):
        # Load the UI from the python file
        QDialog.__init__(self, parent)
        self.ui = Ui_FilterLocationsCustomDialog()
        self.ui.setupUi(self)
