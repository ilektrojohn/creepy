#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtGui import QDialog
from ui.VerifyDeleteDialog import Ui_verifyDeleteDialog


class VerifyDeleteDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.ui = Ui_verifyDeleteDialog()
        self.ui.setupUi(self)
