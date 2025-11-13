#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtCore import QAbstractTableModel
from PyQt4.QtCore import Qt, QVariant


class LocationsTableModel(QAbstractTableModel):
    def __init__(self, locations):
        self.locations = locations
        super(LocationsTableModel, self).__init__()
        
    def rowCount(self, index):
        return len(self.locations)
    
    def columnCount(self, index):
        return 2

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignLeft | Qt.AlignVCenter))
            return QVariant(int(Qt.AlignRight | Qt.AlignVCenter))
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            if section == 0:
                return QVariant('Date')
            elif section == 1:
                return QVariant('Location')
        return QVariant(int(section + 1))
    
    def data(self, index, role):
        location = self.locations[index.row()]
        if index.isValid() and (0 <= index.row() < len(self.locations)) and location: 
            column = index.column()
            if role == Qt.DisplayRole:
                if column == 0:
                    return QVariant(location.datetime.isoformat())
                if column == 1:
                    return QVariant(location.shortName)
        else:
            return QVariant()
    
    def getLocationFromIndex(self, index):
        if index.isValid() and (0 <= index.row() < len(self.locations)):
            return self.locations[index.row()]    
        
    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
