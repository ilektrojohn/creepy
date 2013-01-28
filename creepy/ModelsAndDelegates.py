from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os
 

class PluginConfigurationListModel(QAbstractListModel):
    def __init__(self, plugins, parent=None):
        super(PluginConfigurationListModel, self).__init__(parent)
        self.plugins = plugins
       
        
    def rowCount(self,index):
        return len(self.plugins)
    
    
    def data(self,index,role):
        plugin= self.plugins[index.row()]
        if index.isValid():
            if role == Qt.DisplayRole:
                return QVariant(plugin.name)
            if role == Qt.DecorationRole:
                if plugin.plugin_object.configured:
                    return  QPixmap(os.path.join(os.getcwd(), "creepy", "include", "add.png"))
                else:
                    return  QPixmap(os.path.join(os.getcwd(), "creepy", "include", "analyze.png"))
        else: 
            return QVariant()
        
    
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
                return  QPixmap(os.path.join(os.getcwd(), "creepy", "include", "add.png"))
            if role == Qt.CheckStateRole:
                if plugin:
                    return (Qt.Checked if plugin.name in self.checkedPlugins else Qt.Unchecked)
                    
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
        return Qt.ItemFlags(QAbstractListModel.flags(self, index)|Qt.ItemIsUserCheckable)

    
    
class ProjectWizardPossibleTargetsTable(QAbstractTableModel):
    def __init__(self, targets, parents=None):
        super(ProjectWizardPossibleTargetsTable, self).__init__()
        self.targets = targets
        
    def rowCount(self, index):
        return len(self.targets)
    
    def columnCount(self, index):
        return 3
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
            return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            if section == 0:
                return QVariant("Picture")
            elif section == 1:
                return QVariant("Username")
            elif section == 2:
                return QVariant("Full Name")
            elif section == 3:
                return QVariant("Details")
        return QVariant(int(section + 1))

    
    def data(self, index, role):
        target = self.targets[index.row()]
        if index.isValid() and target:
            if role == Qt.DisplayRole:
                column = index.column()
                if column == 0:
                    picturePath = os.path.join(os.getcwd(), "creepy", "temp", target['targetPicture'])
                    if picturePath and os.path.exists(picturePath):
                        pixmap = QPixmap(picturePath)
                        pixmap.scaled(5, 5, Qt.IgnoreAspectRatio)
                        return pixmap
                    else:
                        pixmap = QPixmap(os.path.join(os.getcwd(), "creepy", "include", "add.png"))
                        pixmap.scaled(5, 5, Qt.IgnoreAspectRatio)
                        return pixmap
                elif column == 1:
                    return QVariant(target['targetUsername'])
                elif column == 2:
                    return QVariant(target['targetFullname'])
                elif column == 3:
                    return QVariant(target['targetDetails'])
            
        else: 
            return QVariant()
        
        
        
        
        
        