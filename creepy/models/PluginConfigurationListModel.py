from PyQt4.QtCore import QVariant, QAbstractListModel, Qt
from PyQt4.Qt import QPixmap
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
                if pluginListItem[1]:
                    return  QPixmap(os.path.join(os.getcwd(),  "include", "add.png"))
                else:
                    return  QPixmap(os.path.join(os.getcwd(), "include", "analyze.png"))
        else: 
            return QVariant()