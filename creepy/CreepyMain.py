import sys
from PyQt4 import QtCore, QtGui, QtWebKit
from CreepyUI import Ui_CreepyMainWindow
from CreepyPluginsConfigurationDialog import Ui_PluginsConfigurationDialog
from CreepyPersonProjectWizard import Ui_newPersonProjectWizard

from yapsy.PluginManager import PluginManagerSingleton
from ModelsAndDelegates import *
from InputPlugin import InputPlugin
import logging
import os

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class CreepyPersonProjectWizard(QtGui.QWizard):
    """ Loads the Person Based Project Wizard from the ui and shows it """
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
        self.PluginManager.locatePlugins()
        self.PluginManager.loadPlugins()
        
        #Load the UI from the python file
        QtGui.QDialog.__init__(self,parent)
        self.ui = Ui_PluginsConfigurationDialog()
        self.ui.setupUi(self)
        #self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        
        
        
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
        self.ui.webPage.mainFrame().setUrl(QtCore.QUrl(os.path.join('file:///',os.getcwd(),'creepy','include', 'map.html')))
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
            pl.append(plugin)
            '''
            Build the configuration page from the available configuration options
            and add the page to the stackwidget
            '''
            page = QtGui.QWidget()
            page.setObjectName(_fromUtf8("page_"+plugin.name))
            scroll = QtGui.QScrollArea()
            scroll.setWidgetResizable(True)
            layout = QtGui.QVBoxLayout()
            titleLabel = QtGui.QLabel(plugin.name+ " Configuration Options")
            layout.addWidget(titleLabel)
            layout.addWidget(scroll)
            layout.addStretch(1)      
            vboxWidget=QtGui.QWidget()
            vboxWidget.setObjectName("vboxwidget_container_"+plugin.name)
            vbox = QtGui.QGridLayout()
            vbox.setObjectName("vbox_container_"+plugin.name)
            gridLayoutRowIndex = 0
            '''
            Load the String options first
            '''
            pluginStringOptions = plugin.plugin_object.readConfiguration("string_options")
            if pluginStringOptions != None:
                for idx, item in enumerate(pluginStringOptions.keys()):
                    
                    label = QtGui.QLabel()
                    label.setObjectName(_fromUtf8("string_label_"+item))
                    label.setText(_fromUtf8(item))
                    vbox.addWidget(label, idx, 0)
                    value = QtGui.QLineEdit()
                    value.setObjectName(_fromUtf8("string_value_"+item))
                    value.setText(pluginStringOptions[item])
                    vbox.addWidget(value, idx, 1)
                    gridLayoutRowIndex = idx +1

                    
                
            '''
            Load the boolean options 
            '''
            pluginBooleanOptions = plugin.plugin_object.readConfiguration("boolean_options")
            if pluginBooleanOptions != None:
                for idx, item in enumerate(pluginBooleanOptions.keys()):
                    cb = QtGui.QCheckBox(item)
                    cb.setObjectName("boolean_label_"+item)
                    if pluginBooleanOptions[item] == 'True':
                        cb.toggle()
                    vbox.addWidget(cb, gridLayoutRowIndex+idx, 0)
                
            
            vboxWidget.setLayout(vbox)
            scroll.setWidget(vboxWidget)
            page.setLayout(layout)
            self.pluginsConfigurationDialog.ui.ConfigurationDetails.addWidget(page)
            
        self.pluginsConfigurationDialog.ui.ConfigurationDetails.setCurrentIndex(0)   
            
        self.PluginListModel = PluginListModel(pl,self)
        self.pluginsConfigurationDialog.ui.PluginsList.setModel(self.PluginListModel)
        QtCore.QObject.connect(self.pluginsConfigurationDialog.ui.PluginsList, QtCore.SIGNAL("clicked(QModelIndex)"), self.changePluginConfigurationPage)
        if self.pluginsConfigurationDialog.exec_():
            self.saveConfiguration()
        
        
           
         
    def saveConfiguration(self):  
        """
        Reads all the configuration options for the plugins and calls the saveConfiguration method of all the plugins.
        """ 
        pages = (self.pluginsConfigurationDialog.ui.ConfigurationDetails.widget(i) for i in range(self.pluginsConfigurationDialog.ui.ConfigurationDetails.count()))
        for page in pages:
            for widg in [ scrollarea.children() for scrollarea in page.children() if type(scrollarea) == QtGui.QScrollArea]:
                for i in widg[0].children():
                    config_options = {}
                    plugin_name = i.objectName().replace("vboxwidget_container_","")
                    string_options = {}
                    for j in i.findChildren(QtGui.QLabel):
                        string_options[str(j.text())] = str(i.findChild(QtGui.QLineEdit, j.objectName().replace("label","value")).text())
                    boolean_options = {}    
                    for k in i.findChildren(QtGui.QCheckBox):
                        boolean_options[str(k.text())] = str(k.isChecked())  
                        
                    config_options['string_options'] = string_options
                    config_options['boolean_options'] = boolean_options            
                    self.pluginsConfigurationDialog.PluginManager.getPluginByName(plugin_name, "Input").plugin_object.saveConfiguration(config_options)  
                
        
        
    def changePluginConfigurationPage(self, modelIndex):
        self.pluginsConfigurationDialog.ui.ConfigurationDetails.setCurrentIndex(modelIndex.row())   
        
    def showPersonProjectWizard(self):
        personProjectWizard = CreepyPersonProjectWizard()
        
        
if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = CreepyMainWindow()
    myapp.show()
    sys.exit(app.exec_())

