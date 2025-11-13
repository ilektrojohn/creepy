#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtCore import QVariant, QAbstractTableModel, Qt
from PyQt4.Qt import QDataStream, QIODevice, QModelIndex


class ProjectWizardSelectedTargetsTable(QAbstractTableModel):
    def __init__(self, targets, parents=None):
        super(ProjectWizardSelectedTargetsTable, self).__init__()
        self.targets = targets

    def rowCount(self, index):
        return len(self.targets)

    def columnCount(self, index):
        return 5

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignLeft | Qt.AlignVCenter))
            return QVariant(int(Qt.AlignRight | Qt.AlignVCenter))
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

        if index.isValid() and target:
            column = index.column()
            if role == Qt.DecorationRole:
                if column == 1:
                    pixmap = target['targetPicture']
                    return pixmap
            if role == Qt.DisplayRole:
                if column == 0:
                    return QVariant(target['pluginName'])
                if column == 1:
                    return QVariant()
                elif column == 2:
                    return QVariant(target['targetUsername'])
                elif column == 3:
                    return QVariant(target['targetFullname'])
                elif column == 4:
                    return QVariant(target['targetUserid'])
            else:
                return QVariant()

    def removeRows(self, rows, count, parent=QModelIndex()):
        for row in rows:
            if row in self.targets:
                self.targets.remove(row)
                self.beginRemoveRows(parent, len(self.targets), len(self.targets))
                self.endRemoveRows()

    def insertRow(self, row, parent=QModelIndex()):
        self.insertRows(row, 1, parent)

    def insertRows(self, rows, count, parent=QModelIndex()):
        for row in rows:
            self.targets.append(row)
            self.beginInsertRows(parent, len(self.targets), len(self.targets))
            self.endInsertRows()
        return True

    def flags(self, index):
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index) | Qt.ItemIsDropEnabled)

    def mimeTypes(self):
        return ['application/target.tableitem.creepy']

    def dropMimeData(self, data, action, row, column, parent):
        if data.hasFormat('application/target.tableitem.creepy'):
            encodedData = data.data('application/target.tableitem.creepy')
            stream = QDataStream(encodedData, QIODevice.ReadOnly)
            columnsList = []
            qVariant = QVariant()
            while not stream.atEnd():
                stream >> qVariant
                columnsList.append(qVariant.toPyObject())
            draggedRows = [columnsList[x:x + 5] for x in range(0, len(columnsList), 5)]
            droppedRows = []
            for row in draggedRows:
                # Ensure we are not putting duplicates in the target list
                existed = False
                for target in self.targets:
                    if row[2] == target['targetUsername'] and row[0] == target['pluginName']:
                        existed = True
                if not existed:
                    droppedRows.append({'targetUsername': row[2], 'targetFullname': row[3], 'targetPicture': row[1],
                                        'targetUserid': row[4], 'pluginName': row[0]})
            self.insertRows(droppedRows, len(droppedRows), parent)

        return True
