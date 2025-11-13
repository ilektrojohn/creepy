#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtCore import QVariant, QAbstractListModel, Qt
from PyQt4.Qt import QPixmap, QIcon
import os
from utilities import GeneralUtilities


class PluginConfigurationListModel(QAbstractListModel):
    def __init__(self, plugins, parent=None):
        super(PluginConfigurationListModel, self).__init__(parent)
        self.plugins = []
        self.pluginList = plugins
    
    def checkPluginConfiguration(self):
        for plugin in self.pluginList:
            self.plugins.append((plugin, True))
        
    def rowCount(self, index):
        return len(self.plugins)
    
    def data(self, index, role):
        pluginListItem= self.plugins[index.row()]
        if index.isValid():
            if role == Qt.DisplayRole:
                return QVariant(pluginListItem[0].name)
            if role == Qt.DecorationRole:
                for directory in GeneralUtilities.getPluginDirs():
                    picturePath = os.path.join(directory, pluginListItem[0].plugin_object.name, 'logo.png')
                    if picturePath and os.path.exists(picturePath):
                        pixmap = QPixmap(picturePath)
                        return QIcon(pixmap)
                pixmap = QPixmap(':/creepy/folder')
                return QIcon(pixmap)
        else: 
            return QVariant()
