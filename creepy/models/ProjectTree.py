#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtCore import QAbstractItemModel
from PyQt4.QtCore import QModelIndex
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QIcon,QPixmap
from PyQt4.QtCore import QVariant


class ProjectTreeModel(QAbstractItemModel):
    def __init__(self, root, parent=None):
        super(ProjectTreeModel, self).__init__(parent)
        self._rootNode = root
        
    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()
            
        return parentNode.childCount()  
     
    def columnCount(self, parent):
        return 1
    
    def data(self, index, role):
        node = index.internalPointer()
        if index.isValid():
            if role == Qt.DisplayRole:
                return QVariant(node.name())
            if role == Qt.DecorationRole:
                if node.nodeType() == 'PROJECT':
                    return QIcon(QPixmap(':/creepy/blue-folder-horizontal.png'))
                if node.nodeType() == "LOCATIONS":
                    return QIcon(QPixmap(':/creepy/marker.png'))
                if node.nodeType() == 'ANALYSIS':
                    return QIcon(QPixmap(':/creepy/receipt-text.png'))
        else:
            return QVariant()
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return 'Projects'
    
    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def index(self, row, column, parent):
        parentNode = self.getNode(parent)
            
        childItem = parentNode.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()
    
    def parent(self, index):
        node = self.getNode(index)
        parentNode = node.parent()
        if parentNode:
            if parentNode == self._rootNode:
                return QModelIndex()
            return self.createIndex(parentNode.row(), 0, parentNode)
        else:
            return QModelIndex()
    
    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
        
        return self._rootNode
    
    def insertRows(self, position, rows, parent=QModelIndex()):
        parentNode = self.getNode(parent)
        self.beginInsertRows(parent, position, position+rows-1)
        for row in range(rows):
            childNode = ProjectTreeNode('newNode')
            success = parentNode.insertChild(childNode, position)
        self.endInsertRows()
        return success
    
    def insertProjects(self, position, rows, parent=QModelIndex()):
        
        parentNode = self.getNode(parent)
        self.beginInsertRows(parent, position, position+rows-1)
        for row in range(rows):
            childNode = ProjectNode('newNode')
            success = parentNode.insertChild(childNode, position)
        self.endInsertRows()
        return success
    
    def removeRows(self, position, rows, parent=QModelIndex()):
        parentNode = self.getNode(parent)
        self.beginRemoveRows(parent, position, position+rows-1)
        for row in range(rows):
            success = parentNode.removeChild(position)
        self.endRemoveRows()
        return success


class ProjectTreeNode(object):
    
    def __init__(self, name, parent=None):
        self._name = name
        self._children = []
        self._parent = parent
        self._type = 'ROOT'
        
        if parent is not None:
            parent.addChild(self)
            
    def name(self):
        return self._name        
            
    def addChild(self, child):
        self._children.append(child)
        
    def insertChild(self, position, child):
        if 0 < position < len(self._children):
            self._children.insert(position, child)
            child._parent = self
            return True
        else:
            return False

    def removeChild(self, position):
        if 0 < position < len(self._children):
            child = self._children.pop(position)
            child._parent = None
            return True
        else:
            return False
        
    def child(self, row):
        return self._children[row]
    
    def childCount(self):
        return len(self._children)
    
    def parent(self):
        return self._parent
    
    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)
        else:
            return 0
        
    def nodeType(self):
        return self._type


class ProjectNode(ProjectTreeNode):
    def __init__(self, name, project, parent=None):
        super(ProjectNode, self).__init__(name, parent)
        self._type = 'PROJECT'
        self.project = project 


class LocationsNode(ProjectTreeNode):
    def __init__(self, name, parent=None):
        super(LocationsNode, self).__init__(name, parent)
        self._type = 'LOCATIONS'
        self.locations = []


class AnalysisNode(ProjectTreeNode):
    def __init__(self, name, parent=None):
        super(AnalysisNode, self).__init__(name, parent)
        self._type = 'ANALYSIS'
        self.analysis = ""

