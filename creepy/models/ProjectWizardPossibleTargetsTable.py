#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtCore import QVariant, QAbstractTableModel, Qt
from PyQt4.Qt import QPixmap, QIcon, QMimeData, QByteArray, QDataStream, QIODevice
import os
class ProjectWizardPossibleTargetsTable(QAbstractTableModel):
    def __init__(self, targets, parents=None):
        super(ProjectWizardPossibleTargetsTable, self).__init__()
        self.targets = targets
        
    def rowCount(self, index):
        return len(self.targets)
    
    def columnCount(self, index):
        return 5
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
            return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            if section == 0:
                return QVariant('Plugin')
            elif section == 1:
                return QVariant('Picture')
            elif section == 2:
                return QVariant('Username')
            elif section == 3:
                return QVariant('Full Name')
            elif section == 4:
                return QVariant('User Id')
        return QVariant(int(section + 1))

    
    def data(self, index, role):
        target = self.targets[index.row()]
        if index.isValid() and (0 <= index.row() < len(self.targets)) and target: 
            column = index.column()
            if role == Qt.DecorationRole:
                if column == 1:
                    picturePath = os.path.join(os.getcwdu(), 'temp', target['targetPicture'])
                    if picturePath and os.path.exists(picturePath):
                        pixmap = QPixmap(picturePath)
                        return QIcon(pixmap.scaled(30, 30, Qt.IgnoreAspectRatio, Qt.FastTransformation))
                    else:
                        pixmap = QPixmap(':/creepy/user')
                        pixmap.scaled(20, 20, Qt.IgnoreAspectRatio)
                        return QIcon(pixmap)
            if role == Qt.DisplayRole:
                if column == 0:
                    return QVariant(target['pluginName'])
                elif column == 1:
                    return QVariant()
                elif column == 2:
                    return QVariant(target['targetUsername'])
                elif column == 3:
                    return QVariant(target['targetFullname'])
                elif column == 4:
                    return QVariant(target['targetUserid'])
                
            
        else: 
            return QVariant()

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index)|Qt.ItemIsDragEnabled|Qt.ItemIsDropEnabled)
        
    def mimeTypes(self):
        return [ 'application/target.tableitem.creepy' ] 
    
    def mimeData(self, indices):
        mimeData = QMimeData()
        encodedData = QByteArray()
        stream = QDataStream(encodedData, QIODevice.WriteOnly)
        for index in indices:
            if index.column() == 1:
                d = QVariant(self.data(index, Qt.DecorationRole))
            else:
                d = QVariant(self.data(index, Qt.DisplayRole).toString())
            stream << d
        mimeData.setData('application/target.tableitem.creepy', encodedData)
        return mimeData