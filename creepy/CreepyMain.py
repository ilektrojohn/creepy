# import main libraries
import sys, datetime, os
import shelve, logging
from PyQt4 import QtCore, QtGui, QtWebKit, Qt
# import the UI
from ui.CreepyUI import Ui_CreepyMainWindow
from ui.CreepyPluginsConfigurationDialog import Ui_PluginsConfigurationDialog
from ui.CreepyPersonProjectWizard import Ui_personProjectWizard
from ui.CreepyPluginConfigurationCheckdialog import Ui_checkPluginConfigurationDialog
from ui.FilterLocationsDateDialog import Ui_FilterLocationsDateDialog
from ui.FilterLocationsPointDialog import Ui_FilteLocationsPointDialog
from ui.AboutDialog import Ui_aboutDialog
import ui.creepy_resources_rc
# import creepy related modules
from yapsy.PluginManager import PluginManagerSingleton
from models.LocationsList import LocationsTableModel
from models.Project import Project
from models.Location import Location
from models.PluginConfigurationListModel import PluginConfigurationListModel
from models.ProjectWizardPluginListModel import ProjectWizardPluginListModel
from models.ProjectWizardPossibleTargetsTable import ProjectWizardPossibleTargetsTable
from models.ProjectWizardSelectedTargetsTable import ProjectWizardSelectedTargetsTable
from models.InputPlugin import InputPlugin
from models.ProjectTree import *
import functools
import webbrowser
import csv
import codecs
import types
from math import radians, cos, sin, asin, sqrt

# set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('creepy_main.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
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
        # Load the UI from the python file
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_checkPluginConfigurationDialog()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

class PersonProjectWizard(QtGui.QWizard):
    """ Loads the Person Based Project Wizard from the ui and shows it """
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.ui = Ui_personProjectWizard()
        self.ui.setupUi(self)
        self.selectedTargets = []
        self.enabledPlugins = []
        # Register the project name field so that it will become mandatory
        self.page(0).registerField('name*', self.ui.personProjectNameValue)
        
    def showWarning(self, title, text):
        QtGui.QMessageBox.warning(self, title, text)
        
    def initializePage(self, i):
        """
        If the page to be loaded is the page containing the search
        options for our plugins, store the selected targets and load the relative search options based on the 
        selected target
        If the page is the search page, set focus to the search button instead of the next
        """
        if i == 2:
            self.storeSelectedTargets()
            self.showPluginsSearchOptions()
        if i == 1:
            self.ui.personProjectSearchButton.setFocus()
        
    
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
        self.PluginManager.setPluginPlaces([os.path.join(os.getcwd(), 'plugins')])
        self.PluginManager.locatePlugins()
        self.PluginManager.loadPlugins()
        pluginList = sorted(self.PluginManager.getAllPlugins(), key=lambda x: x.name)
        return [[plugin, 0] for plugin in pluginList ]
    
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
            page.setObjectName(_fromUtf8("searchconfig_page_" + plugin.name))
            scroll = QtGui.QScrollArea()
            scroll.setWidgetResizable(True)
            layout = QtGui.QVBoxLayout()
            titleLabel = QtGui.QLabel(plugin.name + self.tr(" Search Options"))
            layout.addWidget(titleLabel)    
            vboxWidget = QtGui.QWidget()
            vboxWidget.setObjectName("searchconfig_vboxwidget_container_" + plugin.name)
            vbox = QtGui.QGridLayout()
            vbox.setObjectName("searchconfig_vbox_container_" + plugin.name)
            gridLayoutRowIndex = 0
            '''
            Load the String options first
            '''
            pluginStringOptions = plugin.plugin_object.readConfiguration("search_string_options")[1]
            if pluginStringOptions:
                for idx, item in enumerate(pluginStringOptions.keys()):
                    itemLabel = plugin.plugin_object.getLabelForKey(item)
                    label = QtGui.QLabel()
                    label.setObjectName(_fromUtf8("searchconfig_string_label_" + item))
                    label.setText(_fromUtf8(itemLabel))
                    vbox.addWidget(label, idx, 0)
                    value = QtGui.QLineEdit()
                    value.setObjectName(_fromUtf8("searchconfig_string_value_" + item))
                    value.setText(pluginStringOptions[item])
                    vbox.addWidget(value, idx, 1)
                    gridLayoutRowIndex = idx + 1
           
                    
                
            '''
            Load the boolean options 
            '''
            pluginBooleanOptions = plugin.plugin_object.readConfiguration("search_boolean_options")[1]
            if pluginBooleanOptions:
                for idx, item in enumerate(pluginBooleanOptions.keys()):
                    itemLabel = plugin.plugin_object.getLabelForKey(item)
                    cb = QtGui.QCheckBox(itemLabel)
                    cb.setObjectName("searchconfig_boolean_label_" + item)
                    if pluginBooleanOptions[item] == 'True':
                        cb.toggle()
                    vbox.addWidget(cb, gridLayoutRowIndex + idx, 0)
            #If there are no search options just show a message 
            if not pluginBooleanOptions and not pluginStringOptions:
                label = QtGui.QLabel()
                label.setObjectName(_fromUtf8("no_search_config_options"))
                label.setText(self.tr("This plugin does not offer any search options."))
                vbox.addWidget(label,0,0)
            
            vboxWidget.setLayout(vbox)
            scroll.setWidget(vboxWidget)
            layout.addWidget(scroll)
            layout.addStretch(1)
            page.setLayout(layout)
            self.ui.searchConfiguration.addWidget(page)
            
            
        self.ui.searchConfiguration.setCurrentIndex(0)   
            
        self.SearchConfigPluginConfigurationListModel = PluginConfigurationListModel(pl, self)
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
                    plugin_name = str(i.objectName().replace("searchconfig_vboxwidget_container_", ""))
                    string_options = {}
                    for j in i.findChildren(QtGui.QLabel):
                        if str(j.text()).startswith("searchconfig"):
                            string_options[str(j.objectName().replace("searchconfig_string_label_", ""))] = str(i.findChild(QtGui.QLineEdit, j.objectName().replace("label", "value")).text())
                    boolean_options = {}    
                    for k in i.findChildren(QtGui.QCheckBox):
                        boolean_options[str(k.objectName().replace("searchconfig_boolean_label_", ""))] = str(k.isChecked())  
                    
            enabledPlugins.append({"pluginName":plugin_name, "searchOptions":{'string':string_options, 'boolean':boolean_options}})       
        return enabledPlugins

class FilterLocationsDateDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        # Load the UI from the python file
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_FilterLocationsDateDialog()
        self.ui.setupUi(self)
        
class FilterLocationsPointDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        # Load the UI from the python file
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_FilteLocationsPointDialog()
        self.ui.setupUi(self)
        self.unit = "m"
    
    def onUnitChanged(self, index):
        self.unit = index 

    class pyObj(QtCore.QObject):
        def __init__(self, parent=None):
            QtCore.QObject.__init__(self)
            self.selectedLat = None
            self.selectedLng = None
        @QtCore.pyqtSlot(str)     
        def setLatLng(self, latlng):
            lat, lng = latlng.replace("(", "").replace(")", "").split(",")
            self.lat = float(lat)
            self.lng = float(lng)
            
class AboutDialog(QtGui.QDialog):
    def __init__(self, parent=None):           
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_aboutDialog()
        self.ui.setupUi(self)
        
class PluginsConfigurationDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        
        # Load the installed plugins and read their metadata
        self.PluginManager = PluginManagerSingleton.get()
        self.PluginManager.setCategoriesFilter({ "Input": InputPlugin})
        self.PluginManager.setPluginPlaces([os.path.join(os.getcwd(), 'plugins')])
        self.PluginManager.locatePlugins()
        self.PluginManager.loadPlugins()
        
        # Load the UI from the python file
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_PluginsConfigurationDialog()
        self.ui.setupUi(self)
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
    def checkPluginConfiguration(self, plugin):
        """
        Calls the isConfigured of the selected Plugin and provides a popup window with the result
        """
        self.saveConfiguration()
        checkPluginConfigurationResultDialog = PluginConfigurationCheckdialog()
        isConfigured = plugin.plugin_object.isConfigured()
        if isConfigured[0]:
            checkPluginConfigurationResultDialog.ui.checkPluginConfigurationResultLabel.setText(plugin.name + self.tr(" is correctly configured.") + isConfigured[1])
        else:
            checkPluginConfigurationResultDialog.ui.checkPluginConfigurationResultLabel.setText(plugin.name + self.tr(" is not correctly configured.") + isConfigured[1])
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
                    plugin_name = i.objectName().replace("vboxwidget_container_", "")
                    string_options = {}
                    for j in i.findChildren(QtGui.QLabel):
                        string_options[str(j.objectName().replace("string_label_", ""))] = str(i.findChild(QtGui.QLineEdit, j.objectName().replace("label", "value")).text())
                    boolean_options = {}    
                    for k in i.findChildren(QtGui.QCheckBox):
                        boolean_options[str(k.objectName().replace("boolean_label_", ""))] = str(k.isChecked())  
                        
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
                        location.infowindow = loc['infowindow']
                        location.shortName = loc['shortName']
                        location.updateId()
                        location.visible = True
                        locationsList.append(location)
            # remove duplicates if any
            for l in locationsList:
                if l.id not in [loc.id for loc in self.project.locations]:
                    self.project.locations.append(l)
            # sort on date 
            self.project.locations.sort(key=lambda x: x.datetime, reverse=True)
                   
            self.emit(QtCore.SIGNAL("locations(PyQt_PyObject)"), self.project)
    
    
    
    def __init__(self, parent=None):
        logging.basicConfig(level=logging.DEBUG)
        # Load the UI Class as self.ui
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_CreepyMainWindow()
        self.ui.setupUi(self)
        self.projectsList = []
        '''
        indicates the currently selected project.
        '''
        self.currentProject = None
       
        # Load the map in the mapWebView using GoogleMaps JS API
        
        self.ui.webPage = QtWebKit.QWebPage()
        self.ui.webPage.mainFrame().setUrl(QtCore.QUrl(os.path.join(os.getcwd(), 'include', 'map.html')))
        self.ui.mapWebView.setPage(self.ui.webPage)
        
        # Add the toggleViewActions for the Docked widgets in the View Menu
        self.ui.menuView.addAction(self.ui.dockWProjects.toggleViewAction())
        self.ui.menuView.addAction(self.ui.dockWLocationsList.toggleViewAction())
        self.ui.menuView.addAction(self.ui.dockWCurrentLocationDetails.toggleViewAction())
        # Add the actions to show the PluginConfiguration Dialog
        self.ui.actionPluginsConfiguration.triggered.connect(self.showPluginsConfigurationDialog)
        # Add actions for the "New .." wizards 
        self.ui.actionNewPersonProject.triggered.connect(self.showPersonProjectWizard)
        
        self.ui.actionAnalyzeCurrentProject.triggered.connect(self.analyzeProject)
        self.ui.actionDrawCurrentProject.triggered.connect(self.presentLocations)
        
        self.ui.actionExportCSV.triggered.connect(self.exportProjectCSV)
        self.ui.actionExportKML.triggered.connect(self.exportProjectKML)
        self.ui.actionExportFilteredCSV.triggered.connect(functools.partial(self.exportProjectCSV, filter=True))
        self.ui.actionExportFilteredKML.triggered.connect(functools.partial(self.exportProjectKML, filter=True))
        self.ui.actionDeleteCurrentProject.triggered.connect(self.deleteCurrentProject)
        
        self.ui.actionFilterLocationsDate.triggered.connect(self.showFilterLocationsDateDialog)
        self.ui.actionFilterLocationsPosition.triggered.connect(self.showFilterLocationsPointDialog)
        self.ui.actionRemoveFilters.triggered.connect(self.removeAllFilters)
        self.ui.actionShowHeatMap.toggled.connect(self.toggleHeatMap)
        self.ui.actionReportProblem.triggered.connect(self.reportProblem)
        self.ui.actionAbout.triggered.connect(self.showAboutDialog)
        
        self.ui.actionExit.triggered.connect(self.close)
        
        self.loadProjectsFromStorage()
        
    def showFilterLocationsPointDialog(self):
        filterLocationsPointDialog = FilterLocationsPointDialog()
        filterLocationsPointDialog.ui.mapPage = QtWebKit.QWebPage()
        myPyObj = filterLocationsPointDialog.pyObj()
        filterLocationsPointDialog.ui.mapPage.mainFrame().addToJavaScriptWindowObject("myPyObj", myPyObj)  
        filterLocationsPointDialog.ui.mapPage.mainFrame().setUrl(QtCore.QUrl(os.path.join(os.getcwd(), 'include', 'mapSetPoint.html')))
        filterLocationsPointDialog.ui.radiusUnitComboBox.insertItem(0, QtCore.QString("m"))
        filterLocationsPointDialog.ui.radiusUnitComboBox.insertItem(1, QtCore.QString("km"))
        filterLocationsPointDialog.ui.radiusUnitComboBox.activated[str].connect(filterLocationsPointDialog.onUnitChanged)
        filterLocationsPointDialog.ui.webView.setPage(filterLocationsPointDialog.ui.mapPage)
        
        
        
        filterLocationsPointDialog.show()
        if filterLocationsPointDialog.exec_():
            r = filterLocationsPointDialog.ui.radiusSpinBox.value()
            if filterLocationsPointDialog.unit == "km":
                radius = r * 1000
            else:
                radius = r
            if hasattr(myPyObj, 'lat') and hasattr(myPyObj, 'lng') and radius:
                self.filterLocationsByPoint(myPyObj.lat, myPyObj.lng, radius)
            
            
            
    
                      
    def showFilterLocationsDateDialog(self):
        filterLocationsDateDialog = FilterLocationsDateDialog()
        filterLocationsDateDialog.show()
        if filterLocationsDateDialog.exec_():
            startDateTime = QtCore.QDateTime(filterLocationsDateDialog.ui.stardateCalendarWidget.selectedDate(), filterLocationsDateDialog.ui.startDateTimeEdit.time()).toPyDateTime()
            endDateTime = QtCore.QDateTime(filterLocationsDateDialog.ui.endDateCalendarWidget.selectedDate(), filterLocationsDateDialog.ui.endDateTimeEdit.time()).toPyDateTime()
            if startDateTime > endDateTime:
                self.showWarning("Invalid Dates", "The start date needs to be before the end date.<p> Please try again ! </p>")
            else:
                self.filterLocationsByDate(startDateTime, endDateTime)
            
    def filterLocationsByDate(self, startDate, endDate):
        if not self.currentProject:
            self.showWarning(self.tr("No project selected"), self.tr("Please select a project !"))
            self.ui.statusbar.showMessage(self.tr("Please select a project !"))
            return
        for l in self.currentProject.locations:
            if l.datetime > startDate and l.datetime < endDate:
                l.visible = True
            else:
                l.visible = False
        self.presentLocations([])
    def calcDistance(self, lat1, lng1, lat2, lng2):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        Original Code from Mickael Dunn <Michael.Dunn@mpi.nl> 
        on http://stackoverflow.com/a/4913653/983244
        """
        # convert decimal degrees to radians 
        lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    
        # haversine formula 
        dlng = lng2 - lng1 
        dlat = lat2 - lat1 
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
        c = 2 * asin(sqrt(a)) 
    
        # 6378100 m is the mean radius of the Earth
        meters = 6378100 * c
        return meters     
    def filterLocationsByPoint(self, lat, lng, radius):
        if not self.currentProject:
            self.showWarning(self.tr("No project selected"), self.tr("Please select a project !"))
            self.ui.statusbar.showMessage(self.tr("Please select a project !"))
            return
        for l in self.currentProject.locations:
            if self.calcDistance(float(lat), float(lng), float(l.latitude), float(l.longitude)) > radius:
                l.visible = False
        self.presentLocations([])
        
        
    def removeAllFilters(self):
        if not self.currentProject:
            self.showWarning(self.tr("No project selected"), self.tr("Please select a project !"))
            self.ui.statusbar.showMessage(self.tr("Please select a project !"))
            return
        for l in self.currentProject.locations:
            l.visible = True
        self.presentLocations([])    
    
    
    def reportProblem(self):
        webbrowser.open_new_tab('https://github.com/ilektrojohn/creepy/issues')  
    
    def showAboutDialog(self):
        aboutDialog = AboutDialog()
        aboutDialog.show()
        if aboutDialog.exec_():
            pass
    
    
    def showWarning(self, title, text):
        QtGui.QMessageBox.warning(self, title, text)
    def toggleHeatMap(self, checked):
        mapFrame = self.ui.webPage.mainFrame()
        if checked:
            mapFrame.evaluateJavaScript("showHeatmap()")
            mapFrame.evaluateJavaScript("hideMarkers()")
        else:
            mapFrame.evaluateJavaScript("showMarkers()")
            mapFrame.evaluateJavaScript("hideHeatmap()")
    def hideMarkers(self):
        mapFrame = self.ui.webPage.mainFrame()
        mapFrame.evaluateJavaScript("hideMarkers()")
    def showMarkers(self):
        mapFrame = self.ui.webPage.mainFrame()
        mapFrame.evaluateJavaScript("showMarkers()")      
    def addMarkerToMap(self, mapFrame, location):
        mapFrame.evaluateJavaScript(QtCore.QString("addMarker(" + str(location.latitude) + "," + str(location.longitude) + ",\"" + location.infowindow + "\")"))     
    def centerMap(self, mapFrame, location):
        mapFrame.evaluateJavaScript(QtCore.QString("centerMap(" + str(location.latitude) + "," + str(location.longitude) + ")")) 
    def setMapZoom(self, mapFrame, level):
        mapFrame.evaluateJavaScript(QtCore.QString("setZoom(" + str(level) + ")")) 
    def clearMarkers(self, mapFrame):
        mapFrame.evaluateJavaScript(QtCore.QString("clearMarkers()"))
    
    def deleteCurrentProject(self, project):
        if not project:
            project = self.currentProject
        pr = Project()
        projectName = project.projectName+".db"
        project.deleteProject(projectName)
        self.loadProjectsFromStorage()
    def exportProjectCSV(self, project,filter=False):
        # If the project was not provided explicitly, analyze the currently selected one
        if not project:
            project = self.currentProject
        if not project:
            self.showWarning(self.tr("No project selected"), self.tr("Please select a project first"))
            self.ui.statusbar.showMessage(self.tr("Please select a project first"))
            return
        if not project.locations:
            self.showWarning(self.tr("No locations found"), self.tr("The selected project has no locations to be exported"))
            self.ui.statusbar.showMessage(self.tr("The selected project has no locations to be exported"))
            return
        if project:     
            fileName = QtGui.QFileDialog.getSaveFileName(None, 'Save CSV export as...', os.getcwd(), 'All files (*.*)')
            if fileName:
                try:
                    fileobj = codecs.open(fileName, 'wb', encoding="utf-8")
                    writer = csv.writer(fileobj, quoting=csv.QUOTE_ALL)
                    writer.writerow(('Timestamp', 'Latitude', 'Longitude', 'Location Name', 'Retrieved from', 'Context'))
                    for loc in project.locations:
                        if (filter and loc.visible) or not filter:
                            #handle unicode now that we are writing to a file                            
                            if isinstance(loc.context,unicode):
                                try:
                                    writer.writerow((loc.datetime.strftime("%Y-%m-%d %H:%M:%S %z"), loc.latitude, loc.longitude,loc.shortName.encode("utf-8"), loc.plugin, loc.context.encode("utf-8"))) 
                                except Exception,err:
                                    logger.error(err)
                                    try:
                                        writer.writerow((loc.datetime.strftime("%Y-%m-%d %H:%M:%S %z"), loc.latitude, loc.longitude,loc.shortName.encode("iso-8859-1"), loc.plugin, loc.context.encode("iso-8859-1")))
                                    except Exception, err:
                                        logger.error(err)
                                        writer.writerow((loc.datetime.strftime("%Y-%m-%d %H:%M:%S %z"), loc.latitude, loc.longitude,"Non printable characters in string", loc.plugin, "Non printable characters in string"))
                            else:
                                writer.writerow((loc.datetime.strftime("%Y-%m-%d %H:%M:%S %z"), loc.latitude, loc.longitude,loc.shortName, loc.plugin, loc.context))                 
                    fileobj.close()
                    self.ui.statusbar.showMessage(self.tr("Project Locations have been exported successfully"))
                except Exception, err:
                    logger.error(err)
                    self.ui.statusbar.showMessage(self.tr("Error saving the export."))
                
        else:
            self.showWarning(self.tr("No project selected"), self.tr("Please select a project !"))
            self.ui.statusbar.showMessage(self.tr("Please select a project !"))
            
    def html_escape(self, text):
        html_escape_table = {
                             "&": "&amp;",
                             '"': "&quot;",
                             "'": "&apos;",
                             ">": "&gt;",
                             "<": "&lt;",
                             }
        return "".join(html_escape_table.get(c, c) for c in text)
            
    def exportProjectKML(self, project, filter=False):
        # If the project was not provided explicitly, analyze the currently selected one
        if not project:
            project = self.currentProject
        if not project:
            self.showWarning(self.tr("No project selected"), self.tr("Please select a project first"))
            self.ui.statusbar.showMessage(self.tr("Please select a project first"))
            return
        if not project.locations:
            self.showWarning(self.tr("No locations found"), self.tr("The selected project has no locations to be exported"))
            self.ui.statusbar.showMessage(self.tr("The selected project has no locations to be exported"))
            return
        if project:     
            fileName = QtGui.QFileDialog.getSaveFileName(None, 'Save KML export as...', os.getcwd(), 'All files (*.*)')
            if fileName:
                try:
                    fileobj = codecs.open(fileName, 'wb', encoding="utf-8")
                    # kml is the list to hold all xml attribs. it will be joined in a string later
                    kml = []
                    kml.append('<?xml version=\"1.0\" encoding=\"UTF-8\"?>')
                    kml.append('<kml xmlns=\"http://www.opengis.net/kml/2.2\">') 
                    kml.append('<Document>')
                    kml.append('  <name>%s.kml</name>' % id)
                    for loc in project.locations:
                        if (filter and loc.visible) or not filter:
                            #handle unicode now that we are writing to a file
                            context = loc.context.encode("utf-8") if isinstance(loc.context,unicode) else loc.context
                            kml.append('  <Placemark>')
                            kml.append('  <name>%s</name>' % loc.datetime.strftime("%Y-%m-%d %H:%M:%S %z"))
                            #handle unicode now that we are writing to a file                            
                            if isinstance(loc.context,unicode):
                                try:
                                    kml.append('    <description> %s' % self.html_escape(loc.context.encode("utf-8")))
                                except Exception, err:
                                    logger.error(err)
                                    try:
                                        kml.append('    <description> %s' % self.html_escape(loc.context.encode("iso-8859-1")))
                                    except Exception, err:
                                        logger.error(err)
                                        kml.append('    <description> non printable characters in context')
                            kml.append('    </description>') 
                            kml.append('    <Point>')
                            kml.append('       <coordinates>%s, %s, 0</coordinates>' % (loc.longitude, loc.latitude))
                            kml.append('    </Point>')
                            kml.append('  </Placemark>')
                    kml.append('</Document>')
                    kml.append('</kml>')
                    
                    kml_string = '\n'.join(kml)
                    fileobj.write(kml_string)
                    fileobj.close()
                    self.ui.statusbar.showMessage(self.tr("Project Locations have been exported successfully"))
                except Exception, err:
                    logger.error(err)
                    self.ui.statusbar.showMessage(self.tr("Error saving the export."))
                
        else:
            self.showWarning(self.tr("No project selected"), self.tr("Please select a project !"))
            self.ui.statusbar.showMessage(self.tr("Please select a project !"))
            
    def analyzeProject(self, project):
        """
        This is called when the user clicks on "Analyze Target". It starts the background thread that
        analyzes targets and returns locations
        
        """
        # If the project was not provided explicitly, analyze the currently selected one
        if not project:
            project = self.currentProject
        if project:     
            self.ui.statusbar.showMessage("Analyzing project for locations. Please wait...")
            project.isAnalysisRunning = True
            self.analyzeProjectThreadInstance = self.analyzeProjectThread(project)
            self.connect(self.analyzeProjectThreadInstance, QtCore.SIGNAL("locations(PyQt_PyObject)"), self.projectAnalysisFinished)
            self.analyzeProjectThreadInstance.start()
        else:
            self.showWarning(self.tr("No project selected"), self.tr("Please select a project !"))
       
    def projectAnalysisFinished(self, project):
        '''
        Called when the analysis thread finishes. It saves the project with the locations and draws the map
        '''
        self.ui.statusbar.showMessage("Project Analysis complete !")
        projectNode = ProjectNode(project.projectName, project)
        locationsNode = LocationsNode(self.tr("Locations"), projectNode)
        analysisNode = AnalysisNode(self.tr("Analysis"), projectNode)
        project.isAnalysisRunning = False
        project.storeProject(projectNode)
        
        '''
        If the analysis produced no results whatsoever, inform the user
        '''
        if not project.locations:
            self.showWarning(self.tr("No Locations Found"), self.tr("We could not find any locations for the analyzed project"))
        else:
            self.presentLocations(project.locations)
        
        
        
    def presentLocations(self, locations):
        """
        Also called when the user clicks on "Analyze Target". It redraws the map and populates the location list
        """
        if not locations:
            if not self.currentProject:
                self.showWarning(self.tr("No project selected"), self.tr("Please select a project !"))
                self.ui.statusbar.showMessage(self.tr("Please select a project !"))
                return
            else:
                locations = self.currentProject.locations
        mapFrame = self.ui.webPage.mainFrame()
        self.clearMarkers(mapFrame)
        visibleLocations = []
        if locations:
            for location in locations:
                if location.visible:
                    visibleLocations.append(location)
                    self.addMarkerToMap(mapFrame, location)
            if visibleLocations:
                self.centerMap(mapFrame, visibleLocations[0])
                self.setMapZoom(mapFrame, 15)
        else:
            self.showWarning(self.tr("No locations found"), self.tr("No locations found for the selected project."))
            self.ui.statusbar.showMessage(self.tr("No locations found for the selected project."))       
        
        self.locationsTableModel = LocationsTableModel(visibleLocations) 
        self.ui.locationsTableView.setModel(self.locationsTableModel)
        self.ui.locationsTableView.clicked.connect(self.updateCurrentLocationDetails)
        self.ui.locationsTableView.activated.connect(self.updateCurrentLocationDetails)
        self.ui.locationsTableView.doubleClicked.connect(self.doubleClickLocationItem)
        self.ui.locationsTableView.resizeColumnsToContents()   
        
    def doubleClickLocationItem(self, index):
        location = self.locationsTableModel.locations[index.row()]
        mapFrame = self.ui.webPage.mainFrame()
        self.centerMap(mapFrame, location)
        self.setMapZoom(mapFrame, 18)
        
    def updateCurrentLocationDetails(self, index):
        """
        Called when the user clicks on a location from the location list. It updates the information 
        displayed on the Current Target Details Window
        """
        location = self.locationsTableModel.locations[index.row()]
        self.ui.currentTargetDetailsLocationValue.setText(location.shortName)
        self.ui.currentTargetDetailsDateValue.setText(location.datetime.strftime("%a %b %d,%H:%M:%S %z"))
        self.ui.currentTargetDetailsSourceValue.setText(location.plugin)
        self.ui.currentTargetDetailsContextValue.setText(location.context)
     
        
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
        # Show the stackWidget
        self.pluginsConfigurationDialog = PluginsConfigurationDialog()
        self.pluginsConfigurationDialog.ui.ConfigurationDetails = QtGui.QStackedWidget(self.pluginsConfigurationDialog)
        self.pluginsConfigurationDialog.ui.ConfigurationDetails.setGeometry(QtCore.QRect(260, 10, 511, 561))
        self.pluginsConfigurationDialog.ui.ConfigurationDetails.setObjectName(_fromUtf8("ConfigurationDetails"))
        
        pl = []
        for plugin in sorted(self.pluginsConfigurationDialog.PluginManager.getAllPlugins(), key=lambda x: x.name):
            pl.append(plugin)
            '''
            Build the configuration page from the available configuration options
            and add the page to the stackwidget
            '''
            page = QtGui.QWidget()
            page.setObjectName(_fromUtf8("page_" + plugin.name))
            scroll = QtGui.QScrollArea()
            scroll.setWidgetResizable(True)
            layout = QtGui.QVBoxLayout()
            titleLabel = QtGui.QLabel(plugin.name + self.tr(" Configuration Options"))
            layout.addWidget(titleLabel)    
            vboxWidget = QtGui.QWidget()
            vboxWidget.setObjectName("vboxwidget_container_" + plugin.name)
            vbox = QtGui.QGridLayout()
            vbox.setObjectName("vbox_container_" + plugin.name)
            gridLayoutRowIndex = 0
            '''
            Load the String options first
            '''
            pluginStringOptions = plugin.plugin_object.readConfiguration("string_options")[1]
            if pluginStringOptions != None:
                for idx, item in enumerate(pluginStringOptions.keys()):
                    itemLabel = plugin.plugin_object.getLabelForKey(item)
                    if item.startswith("hidden_"):
                        configName = item.replace("hidden_", "")
                        isHidden = True;
                    else:
                        configName = item
                        isHidden = False;
                    label = QtGui.QLabel()
                    label.setObjectName(_fromUtf8("string_label_" + item))
                    label.setText(itemLabel)
                    vbox.addWidget(label, idx, 0)
                    value = QtGui.QLineEdit()
                    if isHidden:
                        value.setEchoMode(QtGui.QLineEdit.Password)
                    value.setObjectName(_fromUtf8("string_value_" + item))
                    value.setText(pluginStringOptions[item])
                    vbox.addWidget(value, idx, 1)
                    gridLayoutRowIndex = idx + 1

                
            '''
            Load the boolean options 
            '''
            pluginBooleanOptions = plugin.plugin_object.readConfiguration("boolean_options")[1]
            if pluginBooleanOptions != None:
                for idx, item in enumerate(pluginBooleanOptions.keys()):
                    itemLabel = plugin.plugin_object.getLabelForKey(item)
                    cb = QtGui.QCheckBox(itemLabel)
                    cb.setObjectName("boolean_label_" + item)
                    if pluginBooleanOptions[item] == 'True':
                        cb.toggle()
                    vbox.addWidget(cb, gridLayoutRowIndex + idx, 0)
                    gridLayoutRowIndex += 1
            """
            Add the wizard button if the plugin has a configuration wizard
            """
            if plugin.plugin_object.hasWizard:  
                wizardButton = QtGui.QPushButton(self.tr("Run Configuration Wizard"))
                wizardButton.setObjectName("wizardButton_" + plugin.name)
                wizardButton.setToolTip(self.tr("Click here to run the configuration wizard for the plugin"))
                wizardButton.resize(wizardButton.sizeHint())
                wizardButton.clicked.connect(functools.partial(self.wizardButtonPressed, plugin))
                vbox.addWidget(wizardButton, gridLayoutRowIndex + 1, 0)
                
                
            vboxWidget.setLayout(vbox)
            scroll.setWidget(vboxWidget)
            layout.addWidget(scroll)
            layout.addStretch(1)
            
            
            
            
            pluginsConfigButtonContainer = QtGui.QHBoxLayout()
            checkConfigButton = QtGui.QPushButton(self.tr("Test Plugin Configuration")) 
            checkConfigButton.setObjectName(_fromUtf8("checkConfigButton_" + plugin.name))
            checkConfigButton.setToolTip(self.tr("Click here to test the plugin's configuration"))
            checkConfigButton.resize(checkConfigButton.sizeHint())
            checkConfigButton.clicked.connect(functools.partial(self.pluginsConfigurationDialog.checkPluginConfiguration, plugin))
            applyConfigButton = QtGui.QPushButton("Apply Configuration")
            applyConfigButton.setObjectName(_fromUtf8("applyConfigButton_" + plugin.name))
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
            
        self.PluginConfigurationListModel = PluginConfigurationListModel(pl, self)
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
        personProjectWizard.ProjectWizardPluginListModel = ProjectWizardPluginListModel(personProjectWizard.loadConfiguredPlugins(), self)
        personProjectWizard.ui.personProjectAvailablePluginsListView.setModel(personProjectWizard.ProjectWizardPluginListModel)
        personProjectWizard.ui.personProjectSearchButton.clicked.connect(personProjectWizard.searchForTargets)
        
        
        # Creating it here so it becomes available globally in all functions
        personProjectWizard.ProjectWizardSelectedTargetsTable = ProjectWizardSelectedTargetsTable([], self)
        
        
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
            # Now that we have saved the project, reload all projects to be shown in the UI
            self.loadProjectsFromStorage()
       
            
            
    def loadProjectsFromStorage(self):
        """
        Loads all the existing projects from the storage to be shown in the UI
        """
        # Show the exisiting Projects 
        projectsDir = os.path.join(os.getcwd(), 'projects')
        projectFileNames = [ os.path.join(projectsDir, f) for f in os.listdir(projectsDir) if (os.path.isfile(os.path.join(projectsDir, f)) and f.endswith('.db'))]
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
        self.ui.treeViewProjects.clicked.connect(self.currentProjectChanged)
    
    def currentProjectChanged(self, index):
        '''
        Called whenever a project node or one of its children is clicked
        and makes this the currently selected project
        '''
        nodeObject = self.ui.treeViewProjects.selectionModel().selection().indexes()[0].internalPointer()
        if nodeObject.nodeType() == "PROJECT":
            self.currentProject = nodeObject.project
        elif nodeObject.nodeType() == "LOCATIONS":
            self.currentProject = nodeObject.parent().project  
        elif nodeObject.nodeType() == "ANALYSIS":
            self.currentProject = nodeObject.parent().project
    def doubleClickProjectItem(self):
        """
        Called when the user double-clicks on an item in the tree of the existing projects
        """
        nodeObject = self.ui.treeViewProjects.selectionModel().selection().indexes()[0].internalPointer()
        if nodeObject.nodeType() == "PROJECT":
            self.changeMainWidgetPage("map")
        elif nodeObject.nodeType() == "LOCATIONS":
            self.changeMainWidgetPage("map")
           
        elif nodeObject.nodeType() == "ANALYSIS":
            self.changeMainWidgetPage("analysis")
        
    def rightClickMenu(self, pos):
        """
        Called when the user right-clicks somewhere in the area of the existing projects
        """
        # We will not allow multi select so the selectionModel().selection().indexes() will contain only one
        if self.ui.treeViewProjects.selectionModel().selection().count() == 1:
            nodeObject = self.ui.treeViewProjects.selectionModel().selection().indexes()[0].internalPointer()
            if nodeObject.nodeType() == "PROJECT":
                # First make this the current project
                self.currentProject = nodeObject.project
                if nodeObject.project.isAnalysisRunning:
                    self.showWarning(self.tr("Cannot Edit Project"), self.tr("Please wait until analysis is finished before performing further actions on the project"))
                    return
                rightClickMenu = QtGui.QMenu()
                rightClickMenu.addAction(self.ui.actionAnalyzeCurrentProject)
                rightClickMenu.addAction(self.ui.actionDrawCurrentProject)
                rightClickMenu.addAction(self.ui.actionDeleteCurrentProject)
                rightClickMenu.addAction(self.ui.actionExportCSV)
                rightClickMenu.addAction(self.ui.actionExportKML)
                rightClickMenu.addAction(self.ui.actionExportFilteredCSV)
                rightClickMenu.addAction(self.ui.actionExportFilteredKML)
                
                if rightClickMenu.exec_(self.ui.treeViewProjects.viewport().mapToGlobal(pos)):
                    pass
                
               
   
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())

