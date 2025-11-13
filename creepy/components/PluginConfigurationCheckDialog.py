#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtGui import QDialog
from PyQt4.QtCore  import Qt
from ui.PluginConfigCheckdialog import Ui_checkPluginConfigurationDialog


class PluginConfigurationCheckdialog(QDialog):
    """
    Loads the Plugin Configuration Check Dialog that provides information indicating
    if a plugin is configured or not
    """
    def __init__(self, parent=None):
        # Load the UI from the python file
        QDialog.__init__(self, parent)
        self.ui = Ui_checkPluginConfigurationDialog()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
