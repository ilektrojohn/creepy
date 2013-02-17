import sys, datetime
import shelve, logging
from PyQt4 import QtCore, QtGui, QtWebKit
from CreepyUI import Ui_CreepyMainWindow
from CreepyPluginsConfigurationDialog import Ui_PluginsConfigurationDialog
from CreepyPersonProjectWizard import Ui_personProjectWizard
from CreepyPluginConfigurationCheckdialog import Ui_checkPluginConfigurationDialog

from yapsy.PluginManager import PluginManagerSingleton
from ModelsAndDelegates import *
from InputPlugin import InputPlugin
import logging
import functools

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class CreepyPluginConfigurationCheckdialog(QtGui.QDialog):
    def __init__(self, parent=None):
        #Load the UI from the python file
        QtGui.QDialog.__init__(self,parent)
        self.ui = Ui_checkPluginConfigurationDialog()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

class CreepyPersonProjectWizard(QtGui.QWizard):
    """ Loads the Person Based Project Wizard from the ui and shows it """
    def __init__(self,parent=None):
        QtGui.QWizard.__init__(self,parent)
        self.ui = Ui_personProjectWizard()
        self.ui.setupUi(self)
        self.selectedTargets = []
        self.enabledPlugins = []
        #Register the project name field so that it will become mandatory
        self.page(0).registerField('name*', self.ui.personProjectNameValue)
        
    def initializePage(self, i):
        """
        If the page to be loaded is the page containing the search
        options for our plugins, load the relative search options based on the 
        selected targets
        """
        if i == 2:
            self.showPluginsSearchOptions()
        
    def searchForTargets(self):
        selectedPlugins = list(self.ProjectWizardPluginListModel.checkedPlugins)
        possibleTargets = []
        for i in selectedPlugins:
            pluginTargets = self.PluginManager.getPluginByName(i, "Input").plugin_object.searchForTargets()
            if pluginTargets:
                possibleTargets.append(pluginTargets)
            
        self.ProjectWizardPossibleTargetsTable = ProjectWizardPossibleTargetsTable(possibleTargets, self)
        self.ui.personProjectSearchResultsTable.setModel(self.ProjectWizardPossibleTargetsTable)
        
        self.ui.personProjectSelectedTargetsTable.setModel(self.ProjectWizardSelectedTargetsTable)
        
    
    def loadConfiguredPlugins(self):
        #Load the installed plugins and read their metadata
        self.PluginManager = PluginManagerSingleton.get()
        self.PluginManager.setCategoriesFilter({ "Input": InputPlugin})
        self.PluginManager.setPluginPlaces([os.path.join(os.getcwd(), 'creepy', 'plugins')])
        self.PluginManager.locatePlugins()
        self.PluginManager.loadPlugins()
        return [[plugin,0] for plugin in self.PluginManager.getAllPlugins() if plugin.plugin_object.isFunctional()]
            
    def showPluginsSearchOptions(self):
        #List of plugin objects
        pl = []
        for pluginName in list(set([target['plugin'] for target in self.ProjectWizardSelectedTargetsTable.targets])):
            plugin = self.PluginManager.getPluginByName(pluginName, "Input")
            self.enabledPlugins.append(plugin)
            pl.append(plugin)
            '''
            Build the configuration page from the available saerch options
            and add the page to the stackwidget
            '''
            page = QtGui.QWidget()
            page.setObjectName(_fromUtf8("searchconfig_page_"+plugin.name))
            scroll = QtGui.QScrollArea()
            scroll.setWidgetResizable(True)
            layout = QtGui.QVBoxLayout()
            titleLabel = QtGui.QLabel(plugin.name+ " Search Options")
            layout.addWidget(titleLabel)    
            vboxWidget=QtGui.QWidget()
            vboxWidget.setObjectName("searchconfig_vboxwidget_container_"+plugin.name)
            vbox = QtGui.QGridLayout()
            vbox.setObjectName("searchconfig_vbox_container_"+plugin.name)
            gridLayoutRowIndex = 0
            '''
            Load the String options first
            '''
            pluginStringOptions = plugin.plugin_object.readConfiguration("search_string_options")
            if pluginStringOptions != None:
                for idx, item in enumerate(pluginStringOptions.keys()):
                    
                    label = QtGui.QLabel()
                    label.setObjectName(_fromUtf8("searchconfig_string_label_"+item))
                    label.setText(_fromUtf8(item))
                    vbox.addWidget(label, idx, 0)
                    value = QtGui.QLineEdit()
                    value.setObjectName(_fromUtf8("searchconfig_string_value_"+item))
                    value.setText(pluginStringOptions[item])
                    vbox.addWidget(value, idx, 1)
                    gridLayoutRowIndex = idx +1

                    
                
            '''
            Load the boolean options 
            '''
            pluginBooleanOptions = plugin.plugin_object.readConfiguration("search_boolean_options")
            if pluginBooleanOptions != None:
                for idx, item in enumerate(pluginBooleanOptions.keys()):
                    cb = QtGui.QCheckBox(item)
                    cb.setObjectName("searchconfig_boolean_label_"+item)
                    if pluginBooleanOptions[item] == 'True':
                        cb.toggle()
                    vbox.addWidget(cb, gridLayoutRowIndex+idx, 0)
                
            
            vboxWidget.setLayout(vbox)
            scroll.setWidget(vboxWidget)
            layout.addWidget(scroll)
            layout.addStretch(1)
            page.setLayout(layout)
            self.ui.searchConfiguration.addWidget(page)
            
            
        self.ui.searchConfiguration.setCurrentIndex(0)   
            
        self.SearchConfigPluginConfigurationListModel = PluginConfigurationListModel(pl,self)
        self.ui.personProjectWizardSearchConfigPluginsList.setModel(self.SearchConfigPluginConfigurationListModel)
        QtCore.QObject.connect(self.ui.personProjectWizardSearchConfigPluginsList, QtCore.SIGNAL("clicked(QModelIndex)"), self.changePluginConfigurationPage)


    def changePluginConfigurationPage(self, modelIndex):
        self.ui.searchConfiguration.setCurrentIndex(modelIndex.row())   
        
    def readSearchConfiguration(self):  
        """
        Reads all the search configuration options for the enabled plugins and and returns a list of the enabled plugins and their options.
        """ 
        enabledPlugins = []
        pages = (self.ui.searchConfiguration.widget(i) for i in range(self.ui.searchConfiguration.count()))
        for page in pages:
            for widg in [ scrollarea.children() for scrollarea in page.children() if type(scrollarea) == QtGui.QScrollArea]:
                for i in widg[0].children():
                    plugin_name = str(i.objectName().replace("searchconfig_vboxwidget_container_",""))
                    string_options = {}
                    for j in i.findChildren(QtGui.QLabel):
                        string_options[str(j.text())] = str(i.findChild(QtGui.QLineEdit, j.objectName().replace("label","value")).text())
                    boolean_options = {}    
                    for k in i.findChildren(QtGui.QCheckBox):
                        boolean_options[str(k.text())] = str(k.isChecked())  
                    
            enabledPlugins.append({"pluginName":plugin_name,"searchOptions":{'string':string_options, 'boolean':boolean_options}})       
        return enabledPlugins
    
    def storeProject(self, projectObject):
        """
        Receives a projectObject and stores it using the selected data persistence method. 
        Decoupled here for flexibility
        """
        storedProject = shelve.open(projectObject['projectName']+".db")
        try:
            storedProject['project'] = projectObject
        except Exception,err:
            logging.log(logging.ERROR, "Error saving the project : "+err)
        finally:
            storedProject.close()

class CreepyPluginsConfigurationDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        
        #Load the installed plugins and read their metadata
        self.PluginManager = PluginManagerSingleton.get()
        self.PluginManager.setCategoriesFilter({ "Input": InputPlugin})
        self.PluginManager.setPluginPlaces([os.path.join(os.getcwd(), 'creepy', 'plugins')])
        self.PluginManager.locatePlugins()
        self.PluginManager.loadPlugins()
        
        #Load the UI from the python file
        QtGui.QDialog.__init__(self,parent)
        self.ui = Ui_PluginsConfigurationDialog()
        self.ui.setupUi(self)
        #self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
    def checkPluginConfiguration(self, plugin):
        self.saveConfiguration()
        checkPluginConfigurationResultDialog = CreepyPluginConfigurationCheckdialog()
        if plugin.plugin_object.isFunctional():
            checkPluginConfigurationResultDialog.ui.checkPluginConfigurationResultLabel.setText(plugin.name+" is correctly configured.")
        else:
            checkPluginConfigurationResultDialog.ui.checkPluginConfigurationResultLabel.setText(plugin.name+" is not correctly configured. Please try to edit the options and test again.")
        checkPluginConfigurationResultDialog.exec_()
         
    def saveConfiguration(self):  
        """
        Reads all the configuration options for the plugins and calls the saveConfiguration method of all the plugins.
        """ 
        pages = (self.ui.ConfigurationDetails.widget(i) for i in range(self.ui.ConfigurationDetails.count()))
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
                    self.PluginManager.getPluginByName(plugin_name, "Input").plugin_object.saveConfiguration(config_options)  
                
        
        
        
    
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
        for plugin in self.pluginsConfigurationDialog.PluginManager.getAllPlugins():
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
            layout.addWidget(scroll)
            layout.addStretch(1)
            testButtonContainer = QtGui.QHBoxLayout()
            testButton = QtGui.QPushButton("Test Plugin Configuration") 
            testButton.setObjectName(_fromUtf8("testButton_"+plugin.name))
            testButton.setToolTip("Click here to test the plugin's configuration")
            testButton.resize(testButton.sizeHint())
            testButtonContainer.addStretch(1)
            testButtonContainer.addWidget(testButton)
            layout.addLayout(testButtonContainer)
            QtCore.QObject.connect(testButton, QtCore.SIGNAL("clicked()"),functools.partial(self.pluginsConfigurationDialog.checkPluginConfiguration, plugin))
            page.setLayout(layout)
            self.pluginsConfigurationDialog.ui.ConfigurationDetails.addWidget(page)
            
            
        self.pluginsConfigurationDialog.ui.ConfigurationDetails.setCurrentIndex(0)   
            
        self.PluginConfigurationListModel = PluginConfigurationListModel(pl,self)
        self.pluginsConfigurationDialog.ui.PluginsList.setModel(self.PluginConfigurationListModel)
        QtCore.QObject.connect(self.pluginsConfigurationDialog.ui.PluginsList, QtCore.SIGNAL("clicked(QModelIndex)"), self.changePluginConfigurationPage)
        if self.pluginsConfigurationDialog.exec_():
            self.pluginsConfigurationDialog.saveConfiguration()
        
    
    
    def changePluginConfigurationPage(self, modelIndex):
        self.pluginsConfigurationDialog.ui.ConfigurationDetails.setCurrentIndex(modelIndex.row())   
    
    
    
    
    def showPersonProjectWizard(self):
        personProjectWizard = CreepyPersonProjectWizard()
        personProjectObject = {}
        personProjectObject['projectType'] = 'person'
        
        personProjectWizard.ProjectWizardPluginListModel = ProjectWizardPluginListModel(personProjectWizard.loadConfiguredPlugins(),self)
        personProjectWizard.ui.personProjectAvailablePluginsListView.setModel(personProjectWizard.ProjectWizardPluginListModel)
        QtCore.QObject.connect(personProjectWizard.ui.personProjectSearchButton, QtCore.SIGNAL("clicked()"), personProjectWizard.searchForTargets)
        
        #Creating it here so it becomes available globally in all functions
        personProjectWizard.ProjectWizardSelectedTargetsTable = ProjectWizardSelectedTargetsTable([],self)
        
        
        
        
        
        if personProjectWizard.exec_():
            personProjectObject['projectName'] = str(personProjectWizard.ui.personProjectNameValue.text())
            personProjectObject['projectKeywords'] = [keyword.strip() for keyword in str(personProjectWizard.ui.personProjectKeywordsValue.text()).split(",")]
            personProjectObject['projectDescription'] = str(personProjectWizard.ui.personProjectDescriptionValue.toPlainText())
            personProjectObject['enabledPlugins'] = personProjectWizard.readSearchConfiguration()
            personProjectObject['dateCreated'] = datetime.datetime.now()
            personProjectObject['results'] = {}
            personProjectObject['viewSettigns'] = {}
            personProjectWizard.storeProject(personProjectObject)
        else:
            print 'sdsdsda'
if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = CreepyMainWindow()
    myapp.show()
    sys.exit(app.exec_())

