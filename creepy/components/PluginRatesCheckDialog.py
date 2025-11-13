#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtGui import QDialog
from PyQt4.QtCore  import Qt
from ui.PluginRatesCheckDialog import Ui_checkPluginRatesDialog


class PluginRatesCheckDialog(QDialog):
    """
    Loads the Plugin Rates Check Dialog that provides information regarding the API limits of the plugin
    """
    def __init__(self, parent=None):
        # Load the UI from the python file
        QDialog.__init__(self, parent)
        self.ui = Ui_checkPluginRatesDialog()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
