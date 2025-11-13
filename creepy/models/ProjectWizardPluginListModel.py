#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtCore import QVariant, QAbstractListModel, Qt
from PyQt4.Qt import QPixmap, QFileSystemModel, QIcon
from utilities import GeneralUtilities
import os

class ProjectWizardPluginListModel(QAbstractListModel):
    def __init__(self, plugins, parent=None):
        super(ProjectWizardPluginListModel, self).__init__(parent)
        self.plugins = plugins
        self.checkedPlugins = set()
    
    def rowCount(self, index):
        return len(self.plugins)
    
    def data(self, index, role):
        plugin = self.plugins[index.row()][0]
        if index.isValid():
            if role == Qt.DisplayRole:
                return QVariant(plugin.name)
            if role == Qt.DecorationRole:
                for directory in GeneralUtilities.getPluginDirs():
                    picturePath = os.path.join(directory, plugin.plugin_object.name, 'logo.png')
                    if picturePath and os.path.exists(picturePath):
                        pixmap = QPixmap(picturePath)
                        return QIcon(pixmap.scaled(30, 30, Qt.IgnoreAspectRatio, Qt.FastTransformation))
                pixmap = QPixmap(os.path.join(GeneralUtilities.getIncludeDir(), 'generic_plugin.png'))
                pixmap.scaled(30, 30, Qt.IgnoreAspectRatio)
                return QIcon(pixmap)
            if role == Qt.CheckStateRole:
                if plugin:
                    return Qt.Checked if plugin.name in self.checkedPlugins else Qt.Unchecked
                    
        else: 
            return QVariant()
                  
    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.CheckStateRole:
            plugin = self.plugins[index.row()][0]
            if value == Qt.Checked:
                self.checkedPlugins.add(plugin.name)
            else:
                self.checkedPlugins.discard(plugin.name)
            return True
        return QFileSystemModel.setData(self, index, value, role)
                  
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractListModel.flags(self, index) | Qt.ItemIsUserCheckable)
