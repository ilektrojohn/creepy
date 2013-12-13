#import main libraries
import sys, datetime, os
import shelve, logging
from PyQt4 import QtCore, QtGui, QtWebKit, Qt
#import the UI
from CreepyUI import Ui_CreepyMainWindow
from CreepyPluginsConfigurationDialog import Ui_PluginsConfigurationDialog
from CreepyPersonProjectWizard import Ui_personProjectWizard
from CreepyPluginConfigurationCheckdialog import Ui_checkPluginConfigurationDialog
import creepy_resources_rc
#import creepy related modules
from yapsy.PluginManager import PluginManagerSingleton
from ProjectTree import *
from LocationsList import LocationsTableModel
from Project import Project
from Location import Location
from PluginConfigurationListModel import PluginConfigurationListModel
from ProjectWizardPluginListModel import ProjectWizardPluginListModel
from ProjectWizardPossibleTargetsTable import ProjectWizardPossibleTargetsTable
from ProjectWizardSelectedTargetsTable import ProjectWizardSelectedTargetsTable
from InputPlugin import InputPlugin
import functools

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class PluginConfigurationCheckdialog(QtGui.QDialog):
    """
    Loads the Plugin Configuration Check Dialog that provides information indicating
    if a plugin is configured or not
    """
    def __init__(self, parent=None):
        #Load the UI from the python file
        QtGui.QDialog.__init__(self,parent)
        self.ui = Ui_checkPluginConfigurationDialog()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

class PersonProjectWizard(QtGui.QWizard):
    """ Loads the Person Based Project Wizard from the ui and shows it """
    def __init__(self,parent=None):
        QtGui.QWizard.__init__(self,parent)
        self.ui = Ui_personProjectWizard()
        self.ui.setupUi(self)
        self.selectedTargets = []
        self.enabledPlugins = []
        #Register the project name field so that it will become mandatory
        self.page(0).registerField('name*', self.ui.personProjectNameValue)
        
    def showWarning(self, title, text):
        QtGui.QMessageBox.warning(self, title, text)
        
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
        """
        Stores a list of the selected targets for future use
        """
        self.selectedTargets = []
        for target in self.ProjectWizardSelectedTargetsTable.targets:
            self.selectedTargets.append({'pluginName':target['pluginName'],
                                         'targetUsername':target['targetUsername'],
                                         'targetUserid':target['targetUserid'],
                                         'targetFullname':target['targetFullname']
                                         })
             
             
             
    def searchForTargets(self):
        """
        Iterates the selected plugins and for each one performs a search with the given criteria. It
        then populates the PossibleTargets ListModel with the results
        """
        search_term = str(self.ui.personProjectSearchForValue.text())
        if not search_term:
            self.showWarning(self.tr("Empty Search Term"), self.tr("Please enter a search term"))
        else:
            selectedPlugins = list(self.ProjectWizardPluginListModel.checkedPlugins)
            possibleTargets = []
            for i in selectedPlugins:
                pluginTargets = self.PluginManager.getPluginByName(i, "Input").plugin_object.searchForTargets(search_term)
                
                if pluginTargets:
                    possibleTargets.extend(pluginTargets)
                
            self.ProjectWizardPossibleTargetsTable = ProjectWizardPossibleTargetsTable(possibleTargets, self)
            self.ui.personProjectSearchResultsTable.setModel(self.ProjectWizardPossibleTargetsTable)
            
            self.ui.personProjectSelectedTargetsTable.setModel(self.ProjectWizardSelectedTargetsTable)
        
    
    def loadConfiguredPlugins(self):
        """
        Returns a list with the configured plugins that can be used
        """
        self.PluginManager = PluginManagerSingleton.get()
        self.PluginManager.setCategoriesFilter({ "Input": InputPlugin})
        self.PluginManager.setPluginPlaces([os.path.join(os.getcwd(),  'plugins')])
        self.PluginManager.locatePlugins()
        self.PluginManager.loadPlugins()
        return [[plugin,0] for plugin in self.PluginManager.getAllPlugins() ]
    
    def getNameForConfigurationOption(self, key):
        pass
            
    def showPluginsSearchOptions(self):
        """
        Loads the search options of all the selected plugins and populates the relevant UI elements
        with input fields for the string options and checkboxes for the boolean options
        """
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
            titleLabel = QtGui.QLabel(plugin.name+ self.tr(" Search Options"))
            layout.addWidget(titleLabel)    
            vboxWidget=QtGui.QWidget()
            vboxWidget.setObjectName("searchconfig_vboxwidget_container_"+plugin.name)
            vbox = QtGui.QGridLayout()
            vbox.setObjectName("searchconfig_vbox_container_"+plugin.name)
            gridLayoutRowIndex = 0
            '''
            Load the String options first
            '''
            pluginStringOptions = plugin.plugin_object.readConfiguration("search_string_options")[1]
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
            pluginBooleanOptions = plugin.plugin_object.readConfiguration("search_boolean_options")[1]
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
        self.SearchConfigPluginConfigurationListModel.checkPluginConfiguration()
        self.ui.personProjectWizardSearchConfigPluginsList.setModel(self.SearchConfigPluginConfigurationListModel)
        self.ui.personProjectWizardSearchConfigPluginsList.clicked.connect(self.changePluginConfigurationPage)


    def changePluginConfigurationPage(self, modelIndex):
        """
        Called when the user clicks on a plugin in the list of the PluginConfiguration. This shows
        the relevant page with that plugin's configuration options
        """
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

class PluginsConfigurationDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        
        #Load the installed plugins and read their metadata
        self.PluginManager = PluginManagerSingleton.get()
        self.PluginManager.setCategoriesFilter({ "Input": InputPlugin})
        self.PluginManager.setPluginPlaces([os.path.join(os.getcwd(), 'plugins')])
        self.PluginManager.locatePlugins()
        self.PluginManager.loadPlugins()
        
        #Load the UI from the python file
        QtGui.QDialog.__init__(self,parent)
        self.ui = Ui_PluginsConfigurationDialog()
        self.ui.setupUi(self)
        #self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
    def checkPluginConfiguration(self, plugin):
        """
        Calls the isConfigured of the selected Plugin and provides a popup window with the result
        """
        self.saveConfiguration()
        checkPluginConfigurationResultDialog = PluginConfigurationCheckdialog()
        isConfigured =plugin.plugin_object.isConfigured()
        if isConfigured[0]:
            checkPluginConfigurationResultDialog.ui.checkPluginConfigurationResultLabel.setText(plugin.name+self.tr(" is correctly configured.")+isConfigured[1])
        else:
            checkPluginConfigurationResultDialog.ui.checkPluginConfigurationResultLabel.setText(plugin.name+self.tr(" is not correctly configured.")+isConfigured[1])
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
                        string_options[str(j.objectName().replace("string_label_",""))] = str(i.findChild(QtGui.QLineEdit, j.objectName().replace("label","value")).text())
                    boolean_options = {}    
                    for k in i.findChildren(QtGui.QCheckBox):
                        boolean_options[str(k.text())] = str(k.isChecked())  
                        
                    config_options['string_options'] = string_options
                    config_options['boolean_options'] = boolean_options         
                    plugin = self.PluginManager.getPluginByName(plugin_name, "Input")
                    if plugin:
                        plugin.plugin_object.saveConfiguration(config_options)  
                
        
        

        
        
class MainWindow(QtGui.QMainWindow):
    
    class analyzeProjectThread(QtCore.QThread):        
        def __init__(self, project):
            QtCore.QThread.__init__(self)
            self.project = project
        def run(self):
            pluginManager = PluginManagerSingleton.get()
            pluginManager.setCategoriesFilter({ "Input": InputPlugin})
            pluginManager.setPluginPlaces([os.path.join(os.getcwd(), 'plugins')])
            pluginManager.locatePlugins()
            pluginManager.loadPlugins()
            locationsList = []
            for target in self.project.selectedTargets:
                self.emit(QtCore.SIGNAL('update(QString)'), "analyzing target  " + str(target['targetUsername']))
                pluginObject = pluginManager.getPluginByName(target['pluginName'], "Input").plugin_object
                for pl in self.project.enabledPlugins:
                    if pl["pluginName"] == target["pluginName"]:
                        runtimeConfig = pl["searchOptions"] 
                targetLocations = pluginObject.returnLocations(target, runtimeConfig)
                if targetLocations:
                    for loc in targetLocations:
                        location = Location()
                        location.plugin = loc['plugin']
                        location.datetime = loc['date']
                        location.longitude = loc['lon']
                        location.latitude = loc['lat']
                        location.context = loc['context']
                        location.infowindow  = loc['infowindow']
                        location.shortName = loc['shortName']
                        location.updateId()
                        locationsList.append(location)
            #remove duplicates if any
            for l in locationsList:
                if l.id not in [loc.id for loc in self.project.locations]:
                    self.project.locations.append(l)
            #sort on date 
            
                   
            self.emit(QtCore.SIGNAL("locations(PyQt_PyObject)"), self.project)
    
    
    
    def __init__(self,parent=None):
        logging.basicConfig(level=logging.DEBUG)
        # Load the UI Class as self.ui
        QtGui.QWidget.__init__(self,parent)
        self.ui = Ui_CreepyMainWindow()
        self.ui.setupUi(self)
        self.projectsList = []
        
        #Load the map in the mapWebView using GoogleMaps JS API
        
        self.ui.webPage = QtWebKit.QWebPage()
        self.ui.webPage.mainFrame().setUrl(QtCore.QUrl(os.path.join('file:///',os.getcwd(),'include', 'map.html')))
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
    
    def showWarning(self, title, text):
        QtGui.QMessageBox.warning(self, title, text)
        
    def addMarkerToMap(self, mapFrame, location):
        mapFrame.evaluateJavaScript(QtCore.QString("addMarker("+str(location.latitude)+","+str(location.longitude)+",\""+location.infowindow+"\")"))
    def centerMap(self, mapFrame, location):
        mapFrame.evaluateJavaScript(QtCore.QString("centerMap("+str(location.latitude)+","+str(location.longitude)+")")) 
    def setMapZoom(self, mapFrame, level):
        mapFrame.evaluateJavaScript(QtCore.QString("setZoom("+str(level)+")")) 
        
    def clearMarkers(self, mapFrame):
        mapFrame.evaluateJavaScript(QtCore.QString("clearMarkers()")) 
    def analyzeProject(self, project):
        """
        This is called when the user clicks on "Analyze Target". It starts the background thread that
        analyzes targets and returs locations
        
        """ 
        project.isAnalysisRunning = True
        self.analyzeProjectThreadInstance = self.analyzeProjectThread(project)
        self.connect(self.analyzeProjectThreadInstance, QtCore.SIGNAL("locations(PyQt_PyObject)"), self.projectAnalysisFinished )
        self.analyzeProjectThreadInstance.start()
       
    def projectAnalysisFinished(self, project):
        '''
        Called when the analysis thread finishes. It saves the project with the locations and draws the map
        '''
        projectNode = ProjectNode(project.projectName, project)
        locationsNode = LocationsNode(self.tr("Locations"), projectNode)
        analysisNode = AnalysisNode(self.tr("Analysis"), projectNode)
        project.isAnalysisRunning = False
        project.storeProject(projectNode)
        
        '''
        If the analysis produced no results whatsoever, inform the user
        '''
        if not project.locations:
            self.showWarning("No Locations Found", "We could not find any locations for the analyzed project")
        self.presentProject(project)
        
        
        
    def presentProject(self, project):
        """
        Also called when the user clicks on "Analyze Target". It redraws the map and populates the location list
        """
        mapFrame = self.ui.webPage.mainFrame()
        self.clearMarkers(mapFrame)
        for location in project.locations:
            self.addMarkerToMap(mapFrame, location)
            self.centerMap(mapFrame, location)
        
        self.locationsTableModel = LocationsTableModel(project.locations) 
        self.ui.locationsTableView.setModel(self.locationsTableModel)
        self.ui.locationsTableView.clicked.connect(self.updateCurrentLocationDetails)
        self.ui.locationsTableView.doubleClicked.connect(self.doubleClickLocationItem)
        self.ui.locationsTableView.resizeColumnsToContents()   
        
    def doubleClickLocationItem(self, index):
        location =  self.locationsTableModel.locations[index.row()]
        mapFrame = self.ui.webPage.mainFrame()
        self.centerMap(mapFrame, location)
        self.setMapZoom(mapFrame, 15)
        
    def updateCurrentLocationDetails(self,index):
        """
        Called when the user clicks on a location from the location list. It updates the information 
        displayed on the Current Target Details Window
        """
        location =  self.locationsTableModel.locations[index.row()]
        self.ui.currentTargetDetailsLocationValue.setText(location.shortName)
        self.ui.currentTargetDetailsDateValue.setText(location.datetime.isoformat())
        self.ui.currentTargetDetailsSourceValue.setText(location.plugin)
     
        
    def changeMainWidgetPage(self, pageType):
        """
        Changes what is shown in the main window between the map mode and the analysis mode
        """
        if pageType == "map":
            self.ui.centralStackedWidget.setCurrentIndex(0)
        else:
            self.ui.centralStackedWidget.setCurrentIndex(1)  
        
    def wizardButtonPressed(self, plugin):
        """
        This metod calls the wizard of the selected plugin and then reads again the configuration options from file
        for that specific plugin. This happens in order to reflect any changes the wizard might have made to the configuration 
        options.
        
        """    
        plugin.plugin_object.runConfigWizard()
        self.pluginsConfigurationDialog.close()
        self.showPluginsConfigurationDialog()
        
        
   
    def showPluginsConfigurationDialog(self):
        """
        Reads the configuration options for all the plugins, builds the relevant UI items and adds them to the dialog
        """
        #Show the stackWidget
        self.pluginsConfigurationDialog = PluginsConfigurationDialog()
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
            titleLabel = QtGui.QLabel(plugin.name+ self.tr(" Configuration Options"))
            layout.addWidget(titleLabel)    
            vboxWidget=QtGui.QWidget()
            vboxWidget.setObjectName("vboxwidget_container_"+plugin.name)
            vbox = QtGui.QGridLayout()
            vbox.setObjectName("vbox_container_"+plugin.name)
            gridLayoutRowIndex = 0
            '''
            Load the String options first
            '''
            pluginStringOptions = plugin.plugin_object.readConfiguration("string_options")[1]
            if pluginStringOptions != None:
                for idx, item in enumerate(pluginStringOptions.keys()):
                    if item.startswith("hidden_"):
                        configName = item.replace("hidden_", "")
                        isHidden = True;
                    else:
                        configName = item
                        isHidden = False;
                    label = QtGui.QLabel()
                    label.setObjectName(_fromUtf8("string_label_"+item))
                    label.setText(configName)
                    vbox.addWidget(label, idx, 0)
                    value = QtGui.QLineEdit()
                    if isHidden:
                        value.setEchoMode(QtGui.QLineEdit.Password)
                    value.setObjectName(_fromUtf8("string_value_"+item))
                    value.setText(pluginStringOptions[item])
                    vbox.addWidget(value, idx, 1)
                    gridLayoutRowIndex = idx +1

                
            '''
            Load the boolean options 
            '''
            pluginBooleanOptions = plugin.plugin_object.readConfiguration("boolean_options")[1]
            if pluginBooleanOptions != None:
                for idx, item in enumerate(pluginBooleanOptions.keys()):
                    cb = QtGui.QCheckBox(item)
                    cb.setObjectName("boolean_label_"+item)
                    if pluginBooleanOptions[item] == 'True':
                        cb.toggle()
                    vbox.addWidget(cb, gridLayoutRowIndex+idx, 0)
                    gridLayoutRowIndex +=1
            """
            Add the wizard button if the plugin has a configuration wizard
            """
            if plugin.plugin_object.hasWizard:  
                wizardButton= QtGui.QPushButton(self.tr("Run Configuration Wizard"))
                wizardButton.setObjectName("wizardButton_"+plugin.name)
                wizardButton.setToolTip(self.tr("Click here to run the configuration wizard for the plugin"))
                wizardButton.resize(wizardButton.sizeHint())
                wizardButton.clicked.connect(functools.partial(self.wizardButtonPressed, plugin))
                vbox.addWidget(wizardButton, gridLayoutRowIndex+1,0)
                
                
            vboxWidget.setLayout(vbox)
            scroll.setWidget(vboxWidget)
            layout.addWidget(scroll)
            layout.addStretch(1)
            
            
            
            
            pluginsConfigButtonContainer = QtGui.QHBoxLayout()
            checkConfigButton = QtGui.QPushButton(self.tr("Test Plugin Configuration")) 
            checkConfigButton.setObjectName(_fromUtf8("checkConfigButton_"+plugin.name))
            checkConfigButton.setToolTip(self.tr("Click here to test the plugin's configuration"))
            checkConfigButton.resize(checkConfigButton.sizeHint())
            checkConfigButton.clicked.connect(functools.partial(self.pluginsConfigurationDialog.checkPluginConfiguration, plugin))
            applyConfigButton  = QtGui.QPushButton("Apply Configuration")
            applyConfigButton.setObjectName(_fromUtf8("applyConfigButton_"+plugin.name))
            applyConfigButton.setToolTip(self.tr("Click here to save the plugin's configuration options"))
            applyConfigButton.resize(applyConfigButton.sizeHint())
            applyConfigButton.clicked.connect(self.pluginsConfigurationDialog.saveConfiguration)
            pluginsConfigButtonContainer.addStretch(1)
            pluginsConfigButtonContainer.addWidget(applyConfigButton)
            pluginsConfigButtonContainer.addWidget(checkConfigButton)
            layout.addLayout(pluginsConfigButtonContainer)
            
            
            
            
            page.setLayout(layout)
            self.pluginsConfigurationDialog.ui.ConfigurationDetails.addWidget(page)
            
            
        self.pluginsConfigurationDialog.ui.ConfigurationDetails.setCurrentIndex(0)   
            
        self.PluginConfigurationListModel = PluginConfigurationListModel(pl,self)
        self.PluginConfigurationListModel.checkPluginConfiguration()
        self.pluginsConfigurationDialog.ui.PluginsList.setModel(self.PluginConfigurationListModel)
        self.pluginsConfigurationDialog.ui.PluginsList.clicked.connect(self.changePluginConfigurationPage)
        if self.pluginsConfigurationDialog.exec_():
            self.pluginsConfigurationDialog.saveConfiguration()
        
    
    
    def changePluginConfigurationPage(self, modelIndex):
        """
        Changes the page in the PluginConfiguration Dialog depending on which plugin is currently
        selected in the plugin list
        """
        self.pluginsConfigurationDialog.ui.ConfigurationDetails.setCurrentIndex(modelIndex.row())   
    
    
    def showPersonProjectWizard(self):
        """
        Shows the PersonProjectWizard and stores the project information once the wizard is completed
        """
        personProjectWizard = PersonProjectWizard()
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
            project.isAnalysisRunning = False
            project.viewSettigns = {}
            project.selectedTargets = personProjectWizard.selectedTargets
            projectNode = ProjectNode(project.projectName, project)
            locationsNode = LocationsNode(self.tr("Locations"), projectNode)
            analysisNode = AnalysisNode(self.tr("Analysis"), projectNode)
            project.storeProject(projectNode)
            #Now that we have saved the project, reload all projects to be shown in the UI
            self.loadProjectsFromStorage()
       
            
            
    def loadProjectsFromStorage(self):
        """
        Loads all the existing projects from the storage to be shown in the UI
        """
        #Show the exisiting Projects 
        projectsDir = os.path.join(os.getcwd(),'projects')
        projectFileNames = [ os.path.join(projectsDir,f) for f in os.listdir(projectsDir) if (os.path.isfile(os.path.join(projectsDir,f)) and f.endswith('.db'))]
        rootNode = ProjectTreeNode(self.tr("Projects"))
        for projectFile in projectFileNames:
            projectObject = shelve.open(projectFile)
            try:
                rootNode.addChild(projectObject['project'])
            except Exception, err:
                logger.error("Could not read stored project from file")
                logger.exception(err)
        
        self.projectTreeModel = ProjectTreeModel(rootNode) 
        self.ui.treeViewProjects.setModel(self.projectTreeModel)
        self.ui.treeViewProjects.doubleClicked.connect(self.doubleClickProjectItem)
        self.ui.treeViewProjects.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.treeViewProjects.customContextMenuRequested.connect(self.rightClickMenu)
    
    
    def doubleClickProjectItem(self):
        """
        Called when the user double-clicks on an item in the tree of the existing projects
        """
        nodeObject =  self.ui.treeViewProjects.selectionModel().selection().indexes()[0].internalPointer()
        if nodeObject.nodeType() == "PROJECT":
            self.changeMainWidgetPage("map")
        elif nodeObject.nodeType() == "LOCATIONS":
            self.changeMainWidgetPage("map")
            self.presentProject(nodeObject.project)
        elif nodeObject.nodeType() == "ANALYSIS":
            self.changeMainWidgetPage("analysis")
        
    def rightClickMenu(self, pos):
        """
        Called when the user right-clicks somewhere in the area of the existing projects
        """
        rightClickMenu = QtGui.QMenu()
        analyzeProjectAction = QtGui.QAction(QtGui.QIcon(QPixmap(":/cr/analyze.png")), "Analyze Target", self)
        drawLocationsAction = QtGui.QAction(QtGui.QIcon(QPixmap(":/cr/analyze.png")), "Draw Locations", self)
        editProjectAction = QtGui.QAction(QtGui.QIcon(QPixmap(":/cr/project_actionmenu_edit.png")), "Edit Project", self)
        deleteProjectAction = QtGui.QAction(QtGui.QIcon(QPixmap(":/cr/project_actionmenu_delete.png")), "Delete Project", self)
        #We will not allow multi select so the selectionModel().selection().indexes() will contain only one
        if self.ui.treeViewProjects.selectionModel().selection().count() == 1:
            nodeObject =  self.ui.treeViewProjects.selectionModel().selection().indexes()[0].internalPointer()
           
            if nodeObject.nodeType() == "PROJECT":
                rightClickMenu.addAction(analyzeProjectAction)
                rightClickMenu.addAction(drawLocationsAction)
                rightClickMenu.addAction(editProjectAction)
                rightClickMenu.addAction(deleteProjectAction)
                action = rightClickMenu.exec_(self.ui.treeViewProjects.viewport().mapToGlobal(pos))
                if action == analyzeProjectAction:
                    if nodeObject.project.isAnalysisRunning:
                        self.showWarning(self.tr("Cannot Edit Project"), self.tr("Please wait until analysis is finished before performing further actions on the project"))
                    else:
                        self.analyzeProject(nodeObject.project)
                if action == drawLocationsAction:
                    if nodeObject.project.locations:
                        self.presentProject(nodeObject.project)
                    else:
                        self.showWarning(self.tr("No locations found"), self.tr("There are no locations found for this project. PLease run the analysis first"))
                elif action == deleteProjectAction:
                    project = Project()
                    projectName = nodeObject.project.projectName+".db"
                    project.deleteProject(projectName)
                    self.loadProjectsFromStorage()
                elif action == editProjectAction:
                    pass
        
        
if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())

