from PyQt4.QtCore import QVariant, QAbstractTableModel, Qt
import os

class InputPluginTable(QAbstractTableModel):
    def __init__(self, plugins, parents=None):
        super(InputPluginTable, self).__init__()
        self.plugins = plugins
        
    def rowCount(self, index):
        return len(self.targets)
    
    def columnCount(self, index):
        return 4
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
            return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            if section == 0:
                return QVariant("Plugin Name")
            elif section == 1:
                return QVariant("Author")
            elif section == 2:
                return QVariant("Version")
            elif section == 3:
                return QVariant("Description")
        return QVariant(int(section + 1))
    
    
    def data(self, index, role):
        plugin = self.plugins[index.row()]
        if index.isValid() and (0 <= index.row() < len(self.plugins)) and plugin: 
            column = index.column()
            if role == Qt.DisplayRole:
                if column == 0:
                    return QVariant(plugin['name'])
                elif column == 1:
                    return QVariant(plugin['author'])
                elif column == 2:
                    return QVariant(plugin['version'])
                elif column == 3:
                    return QVariant(plugin['description'])
        else: 
            return QVariant()
