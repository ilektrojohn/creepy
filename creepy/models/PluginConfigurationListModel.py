#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtCore import QVariant, QAbstractListModel, Qt
from PyQt4.Qt import QPixmap, QIcon
import os

class PluginConfigurationListModel(QAbstractListModel):
    def __init__(self, plugins, parent=None):
        super(PluginConfigurationListModel, self).__init__(parent)
        self.plugins = []
        self.pluginList = plugins
    
    def checkPluginConfiguration(self):
        for plugin in self.pluginList:
            self.plugins.append((plugin,True))
            '''
            if plugin.plugin_object.isConfigured()[0]:
                self.plugins.append((plugin,True))
            else:
                self.plugins.append((plugin,False))
            '''
        
    def rowCount(self,index):
        return len(self.plugins)
    
    def data(self,index,role):
        pluginListItem= self.plugins[index.row()]
        if index.isValid():
            if role == Qt.DisplayRole:
                return QVariant(pluginListItem[0].name)
            if role == Qt.DecorationRole:
                picturePath = os.path.join(os.getcwdu(), 'plugins', pluginListItem[0].plugin_object.name, 'logo.png')
                if picturePath and os.path.exists(picturePath):
                    pixmap = QPixmap(picturePath)
                    return QIcon(pixmap)
                else:
                    pixmap = QPixmap(':/creepy/folder')
                    return QIcon(pixmap)
        else: 
            return QVariant()