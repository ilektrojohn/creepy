import sys
from PyQt4 import QtCore, QtGui, QtWebKit
from CreepyUI import Ui_CreepyMainWindow
from CreepyPluginsConfigurationDialog import Ui_PluginsConfigurationDialog
from CreepyPersonProjectWizard import Ui_newPersonProjectWizard

from yapsy.PluginManager import PluginManagerSingleton
from CreepyModels import *
from InputPlugin import InputPlugin
import logging

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class CreepyPersonProjectWizard(QtGui.QWizard):
    def __init__(self,parent=None):
        QtGui.QWizard.__init__(self,parent)
        self.ui = Ui_newPersonProjectWizard()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.exec_()
        
class CreepyPluginsConfigurationDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        
        #Load the installed plugins and read their metadata
        self.PluginManager = PluginManagerSingleton.get()
        self.PluginManager.setCategoriesFilter({ "Input": InputPlugin})
        self.PluginManager.setPluginPlaces(["/home/ioannis/code/creepy/creepy/plugins"])
        print self.PluginManager.locatePlugins()
        self.PluginManager.loadPlugins()
        #Set the necessary fields for each plugin in a new page in the StackedWidget
        
        #Load the UI from the python file
        QtGui.QDialog.__init__(self,parent)
        self.ui = Ui_PluginsConfigurationDialog()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        
        
        
    def loadInstalledPlugins(self):
        pass
        
    def drawConfigurationPages(self, installedPlugins):
        pass
    
class CreepyMainWindow(QtGui.QMainWindow):
    def __init__(self,parent=None):
        logging.basicConfig(level=logging.DEBUG)
        # Load the UI Class as self.ui
        QtGui.QWidget.__init__(self,parent)
        self.ui = Ui_CreepyMainWindow()
        self.ui.setupUi(self)
        
        #Load the map in the mapWebView using GoogleMaps JS API
        self.ui.webPage = QtWebKit.QWebPage()
        self.ui.webPage.mainFrame().setUrl(QtCore.QUrl(_fromUtf8("file:///home/ioannis/code/creepy_dev/test.html")))
        self.ui.mapWebView.setPage(self.ui.webPage)
        
        # Add the toggleViewActions for the Docked widgets in the View Menu
        self.ui.menuView.addAction(self.ui.dockWProjects.toggleViewAction())
        self.ui.menuView.addAction(self.ui.dockWLocationsList.toggleViewAction())
        self.ui.menuView.addAction(self.ui.dockWCurrentTargetDetails.toggleViewAction())
        #Add the actions to show the PluginConfiguration Dialog
        self.ui.actionPluginsConfiguration.triggered.connect(self.showPluginsConfigurationDialog)
        
        #Add actions for the "New .." wizards 
        self.ui.actionNewPersonProject.triggered.connect(self.showPersonProjectWizard)
        
        
    def showPluginsConfigurationDialog(self):
        #Show the stackWidget
        self.pluginsConfigurationDialog = CreepyPluginsConfigurationDialog()
        self.pluginsConfigurationDialog.ui.ConfigurationDetails = QtGui.QStackedWidget(self.pluginsConfigurationDialog)
        self.pluginsConfigurationDialog.ui.ConfigurationDetails.setGeometry(QtCore.QRect(260, 10, 511, 561))
        self.pluginsConfigurationDialog.ui.ConfigurationDetails.setObjectName(_fromUtf8("ConfigurationDetails"))
        
        pl = []
        for plugin in self.pluginsConfigurationDialog.PluginManager.getPluginsOfCategory("Input"):
            
            pl.append(plugin.plugin_object.name)
            '''
            Build the configuration page from the available configuration options
            and add the page to the stackwidget
            '''
            page = QtGui.QWidget()
            page.setObjectName(_fromUtf8(plugin.plugin_object.name))
            scroll = QtGui.QScrollArea()
            scroll.setWidgetResizable(True)
            layout = QtGui.QVBoxLayout()
            layout.setMargin(5)
            layout.addWidget(scroll)
            w=QtGui.QWidget()        
            vbox=QtGui.QVBoxLayout(w)
            '''
            Load the String options first
            '''
            pluginStringOptions = plugin.plugin_object.readConfiguration("string_options")
            if pluginStringOptions != None:
                for item in pluginStringOptions.keys():
                    horizontalPropertyContainer = QtGui.QHBoxLayout()
                    label = QtGui.QLabel()
                    label.setObjectName(_fromUtf8(item+"_label"))
                    label.setText(_fromUtf8(item))
                    horizontalPropertyContainer.addWidget(label)
                    value = QtGui.QLineEdit()
                    value.setObjectName(_fromUtf8(item+"_value"))
                    value.setText(pluginStringOptions[item])
                    horizontalPropertyContainer.addWidget(value)
                    vbox.addLayout(horizontalPropertyContainer)
                
            '''
            Load the boolean options 
            '''
            pluginBooleanOptions = plugin.plugin_object.readConfiguration("boolean_options")
            if pluginBooleanOptions != None:
                for item in pluginBooleanOptions.keys():
                    cb = QtGui.QCheckBox(item)
                    if pluginBooleanOptions[item] == 'True':
                        cb.toggle()
                    vbox.addWidget(cb)
                
            
            
            '''
            Load the filepath options if any
            '''
            pluginStringOptions = plugin.plugin_object.readConfiguration("path_options")
            if pluginStringOptions != None:
                for item in pluginStringOptions.keys():
                    horizontalPropertyContainer = QtGui.QHBoxLayout()
                    label = QtGui.QLabel()
                    label.setObjectName(_fromUtf8(item+"_label"))
                    label.setText(_fromUtf8(item))
                    horizontalPropertyContainer.addWidget(label)
                    value = QtGui.QLineEdit()
                    value.setObjectName(_fromUtf8(item+"_value"))
                    value.setText(pluginStringOptions[item])
                    horizontalPropertyContainer.addWidget(value)
                    vbox.addLayout(horizontalPropertyContainer)
            
            scroll.setWidget(w)
            page.setLayout(layout)
            self.pluginsConfigurationDialog.ui.ConfigurationDetails.addWidget(page)
            
        self.pluginsConfigurationDialog.ui.ConfigurationDetails.setCurrentIndex(0)   
            
        self.PluginListModel = PluginModel(pl,self)
        self.pluginsConfigurationDialog.ui.PluginsList.setModel(self.PluginListModel)
        QtCore.QObject.connect(self.pluginsConfigurationDialog.ui.PluginsList, QtCore.SIGNAL("clicked(QModelIndex)"), self.testClick)
        
        
        
        if self.pluginsConfigurationDialog.exec_():
            print 's'
            
    def testClick(self, modelIndex):
        self.pluginsConfigurationDialog.ui.ConfigurationDetails.setCurrentIndex(modelIndex.row())   
        
    def showPersonProjectWizard(self):
        personProjectWizard = CreepyPersonProjectWizard()
        
        
if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = CreepyMainWindow()
    myapp.show()
    sys.exit(app.exec_())

