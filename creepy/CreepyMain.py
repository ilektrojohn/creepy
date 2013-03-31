import sys, datetime
import shelve, logging
import pprint
from PyQt4 import QtCore, QtGui, QtWebKit
from CreepyUI import Ui_CreepyMainWindow
from CreepyPluginsConfigurationDialog import Ui_PluginsConfigurationDialog
from CreepyPersonProjectWizard import Ui_personProjectWizard
from CreepyPluginConfigurationCheckdialog import Ui_checkPluginConfigurationDialog
import creepy_resources_rc
from yapsy.PluginManager import PluginManagerSingleton
from ProjectTree import *
from LocationsList import *
from Project import Project
from Location import Location
from ModelsAndDelegates import *
from InputPlugin import InputPlugin
import logging
import functools
from ubuntuone.syncdaemon.sync import loglevel

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
        options for our plugins, store the selected targets and load the relative search options based on the 
        selected targets
        """
        if i == 2:
            self.storeSelectedTargets()
            self.showPluginsSearchOptions()
        
    
    def storeSelectedTargets(self):
        self.selectedTargets = []
        for target in self.ProjectWizardSelectedTargetsTable.targets:
            self.selectedTargets.append({'pluginName':str(target['pluginName']),'targetUsername':str(target['targetUsername'])})
             
             
             
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
        for pluginName in list(set([target['pluginName'] for target in self.ProjectWizardSelectedTargetsTable.targets])):
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
        self.ui.personProjectWizardSearchConfigPluginsList.clicked.connect(self.changePluginConfigurationPage)


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
        projectName = projectObject.name()+".db"
        print(os.path.join(os.getcwd(),"creepy","projects",projectName))
        
        storedProject = shelve.open(os.path.join(os.getcwd(),"creepy","projects",projectName))
        try:
            storedProject['project'] = projectObject
        except Exception,err:
            logging.log(logging.ERROR, "Error saving the project ")
            logging.exception(err)
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
        self.projectsList = []
        
        #Load the map in the mapWebView using GoogleMaps JS API
        
        self.ui.webPage = QtWebKit.QWebPage()
        self.ui.webPage.mainFrame().setUrl(QtCore.QUrl(os.path.join('file:///',os.getcwd(),'creepy','include', 'map.html')))
        self.ui.mapWebView.setPage(self.ui.webPage)
        
        # Add the toggleViewActions for the Docked widgets in the View Menu
        self.ui.menuView.addAction(self.ui.dockWProjects.toggleViewAction())
        self.ui.menuView.addAction(self.ui.dockWLocationsList.toggleViewAction())
        self.ui.menuView.addAction(self.ui.dockWCurrentLocationDetails.toggleViewAction())
        #Add the actions to show the PluginConfiguration Dialog
        self.ui.actionPluginsConfiguration.triggered.connect(self.showPluginsConfigurationDialog)
        
        #Add actions for the "New .." wizards 
        self.ui.actionNewPersonProject.triggered.connect(self.showPersonProjectWizard)
        
        self.loadProjectsFromStorage()
        
        
    def analyzeProject(self, project):
        pluginManager = PluginManagerSingleton.get()
        pluginManager.setCategoriesFilter({ "Input": InputPlugin})
        pluginManager.setPluginPlaces([os.path.join(os.getcwd(), 'creepy', 'plugins')])
        pluginManager.locatePlugins()
        pluginManager.loadPlugins()
        locationsList = []
        for target in project.selectedTargets:
            pluginObject = pluginManager.getPluginByName(target['pluginName'], "Input").plugin_object
            for pl in project.enabledPlugins:
                if pl["pluginName"] == target["pluginName"]:
                    runtimeConfig = pl["searchOptions"] 
            targetLocations = pluginObject.returnLocations(target, runtimeConfig)
            if targetLocations:
                for loc in targetLocations:
                    location = Location()
                    location.datetime = loc['date']
                    location.longitude = loc['lon']
                    location.latitude = loc['lat']
                    location.context = loc['context']
                    location.shortName = loc['shortName']
                    locationsList.append(location)
                #####CONTINUE HERE#######
        
        project.locations.extend(locationsList)
        
    
    def presentProject(self, project):
        mapFrame = self.ui.webPage.mainFrame()
        for location in project.locations:
            mapFrame.evaluateJavaScript(QString("addMarker("+str(location.latitude)+","+str(location.longitude)+",\""+str(location.shortName)+"\")"))
            print QString("addMarker("+str(location.latitude)+","+str(location.longitude)+","+str(location.shortName)+")")
            mapFrame.evaluateJavaScript(QString("centerMap("+str(location.latitude)+","+str(location.longitude)+")"))
        
        locationsTableModel = LocationsTableModel(project.locations) 
        self.ui.locationsTableView.setModel(locationsTableModel)
        self.ui.locationsTableView.resizeColumnsToContents()   
            
    def changeMainWidgetPage(self, pageType):
        if pageType == "map":
            self.ui.centralStackedWidget.setCurrentIndex(0)
        else:
            self.ui.centralStackedWidget.setCurrentIndex(1)  
             
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
            testButton.clicked.connect(functools.partial(self.pluginsConfigurationDialog.checkPluginConfiguration, plugin))
            page.setLayout(layout)
            self.pluginsConfigurationDialog.ui.ConfigurationDetails.addWidget(page)
            
            
        self.pluginsConfigurationDialog.ui.ConfigurationDetails.setCurrentIndex(0)   
            
        self.PluginConfigurationListModel = PluginConfigurationListModel(pl,self)
        self.pluginsConfigurationDialog.ui.PluginsList.setModel(self.PluginConfigurationListModel)
        self.pluginsConfigurationDialog.ui.PluginsList.clicked.connect(self.changePluginConfigurationPage)
        if self.pluginsConfigurationDialog.exec_():
            self.pluginsConfigurationDialog.saveConfiguration()
        
    
    
    def changePluginConfigurationPage(self, modelIndex):
        self.pluginsConfigurationDialog.ui.ConfigurationDetails.setCurrentIndex(modelIndex.row())   
    
    
    
    
    def showPersonProjectWizard(self):
        personProjectWizard = CreepyPersonProjectWizard()
        
        personProjectWizard.ProjectWizardPluginListModel = ProjectWizardPluginListModel(personProjectWizard.loadConfiguredPlugins(),self)
        personProjectWizard.ui.personProjectAvailablePluginsListView.setModel(personProjectWizard.ProjectWizardPluginListModel)
        personProjectWizard.ui.personProjectSearchButton.clicked.connect(personProjectWizard.searchForTargets)
        
        #Creating it here so it becomes available globally in all functions
        personProjectWizard.ProjectWizardSelectedTargetsTable = ProjectWizardSelectedTargetsTable([],self)
        
        
        if personProjectWizard.exec_():
            project = Project()
            project.projectName = str(personProjectWizard.ui.personProjectNameValue.text())
            project.projectKeywords = [keyword.strip() for keyword in str(personProjectWizard.ui.personProjectKeywordsValue.text()).split(",")]
            project.projectDescription = str(personProjectWizard.ui.personProjectDescriptionValue.toPlainText())
            project.enabledPlugins = personProjectWizard.readSearchConfiguration()
            project.dateCreated = datetime.datetime.now()
            project.dateEdited = datetime.datetime.now()
            project.locations = []
            project.analysis = None
            project.viewSettigns = {}
            project.selectedTargets = personProjectWizard.selectedTargets
            projectNode = ProjectNode(project.projectName, project)
            
            locationsNode = LocationsNode("Locations", projectNode)
            analysisNode = AnalysisNode("Analysis", projectNode)
            personProjectWizard.storeProject(projectNode)
            self.loadProjectsFromStorage()
        else:
            print 'sdsdsda'
            
            
    def loadProjectsFromStorage(self):
        #Show the exisiting Projects 
        projectsDir = os.path.join(os.getcwd(),'creepy','projects')
        projectFileNames = [ os.path.join(projectsDir,f) for f in os.listdir(projectsDir) if (os.path.isfile(os.path.join(projectsDir,f)) and f.endswith('.db'))]
        rootNode = ProjectTreeNode("Projects")
        for projectFile in projectFileNames:
            projectObject = shelve.open(projectFile)
            try:
                rootNode.addChild(projectObject['project'])
            except Exception, err:
                logging.log(logging.ERROR, "Could not read stored project from file")
                logging.exception(err)
        
        self.projectTreeModel = ProjectTreeModel(rootNode) 
        self.ui.treeViewProjects.setModel(self.projectTreeModel)
        self.ui.treeViewProjects.doubleClicked.connect(self.doubleClickItem)
        self.ui.treeViewProjects.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.treeViewProjects.customContextMenuRequested.connect(self.rightClickMenu)
        
    def doubleClickItem(self):
        nodeObject =  self.ui.treeViewProjects.selectionModel().selection().indexes()[0].internalPointer()
        if nodeObject.nodeType() == "PROJECT" or nodeObject.nodeType() == "LOCATIONS":
            self.changeMainWidgetPage("map")
        if nodeObject.nodeType() == "ANALYSIS":
            self.changeMainWidgetPage("analysis")
        
    def rightClickMenu(self, pos):
        #We will not allow multi select so the selectionModel().selection().indexes() will contain only one
        if self.ui.treeViewProjects.selectionModel().selection().count() == 1:
            nodeObject =  self.ui.treeViewProjects.selectionModel().selection().indexes()[0].internalPointer()
           
            rightClickMenu = QMenu()
            analyzeProjectAction = QtGui.QAction(QtGui.QIcon(QPixmap(":/cr/analyze.png")), "Analyze Target", self)
            editProjectAction = QtGui.QAction(QtGui.QIcon(QPixmap(":/cr/project_actionmenu_edit.png")), "Edit Project", self)
            deleteProjectAction = QtGui.QAction(QtGui.QIcon(QPixmap(":/cr/project_actionmenu_delete.png")), "Delete Project", self)
            if nodeObject.nodeType() == "PROJECT":
                rightClickMenu.addAction(analyzeProjectAction)
                rightClickMenu.addAction(editProjectAction)
                rightClickMenu.addAction(deleteProjectAction)
                
            
            action = rightClickMenu.exec_(self.ui.treeViewProjects.viewport().mapToGlobal(pos))
            if action == analyzeProjectAction:
                print nodeObject.project.locations
                self.analyzeProject(nodeObject.project)
                print nodeObject.project.locations
                self.presentProject(nodeObject.project)
        
        
if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = CreepyMainWindow()
    myapp.show()
    sys.exit(app.exec_())

