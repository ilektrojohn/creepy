#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtGui import QDialog
from ui.UpdateCheckDialog import Ui_UpdateCheckDialog
class UpdateCheckDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.ui = Ui_UpdateCheckDialog()
        self.ui.setupUi(self)