from PyQt4 import QtCore
 

class PluginModel(QtCore.QAbstractListModel):
    def __init__(self, plugins, parent=None):
        super(PluginModel, self).__init__(parent)
        self.plugins = plugins
        
    def rowCount(self,index):
        return len(self.plugins)
    
    def data(self,index,role):
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.plugins[index.row()])
        else: 
            return QtCore.QVariant()