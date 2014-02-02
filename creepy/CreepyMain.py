#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import datetime
import os
import logging
import shelve
import functools
import csv
import urllib2
from distutils.version import StrictVersion
from configobj import ConfigObj
from PyQt4.QtCore import QString, QThread, SIGNAL, QUrl, QDateTime, QDate, QRect, Qt
from PyQt4.QtGui import QMainWindow, QApplication, QMessageBox, QFileDialog, QWidget, QScrollArea, QVBoxLayout, QIcon, QPixmap
from PyQt4.QtGui import QHBoxLayout, QLabel, QLineEdit, QCheckBox, QPushButton, QStackedWidget,QGridLayout, QMenu, QTableWidgetItem
from PyQt4.QtWebKit import QWebPage
from ui.CreepyUI import Ui_CreepyMainWindow
from yapsy.PluginManager import PluginManagerSingleton
from models.LocationsList import LocationsTableModel
from models.Project import Project
from models.Location import Location
from models.PluginConfigurationListModel import PluginConfigurationListModel
from models.ProjectWizardPluginListModel import ProjectWizardPluginListModel
from models.ProjectWizardSelectedTargetsTable import ProjectWizardSelectedTargetsTable
from models.InputPlugin import InputPlugin
from models.ProjectTree import ProjectNode, LocationsNode, ProjectTreeModel,ProjectTreeNode
from components.PersonProjectWizard import PersonProjectWizard
from components.PluginsConfigurationDialog import PluginsConfigurationDialog
from components.FilterLocationsDateDialog import FilterLocationsDateDialog
from components.FilterLocationsPointDialog import FilterLocationsPointDialog
from components.AboutDialog import AboutDialog
from components.VerifyDeleteDialog import VerifyDeleteDialog
from components.UpdateCheckDialog import UpdateCheckDialog
from utilities import GeneralUtilities
# set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(os.path.join(os.getcwd(),'creepy_main.log'))
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
#Capture stderr and stdout to a file
sys.stdout = open(os.path.join(os.getcwd(),'creepy_stdout.log'), 'w')
sys.stderr = open(os.path.join(os.getcwd(),'creepy_stderr.log'), 'w')
try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

                       
class MainWindow(QMainWindow):
    
    class analyzeProjectThread(QThread):
        def __init__(self, project):
            QThread.__init__(self)
            self.project = project
        def run(self):
            pluginManager = PluginManagerSingleton.get()
            pluginManager.setCategoriesFilter({ 'Input': InputPlugin})
            pluginManager.setPluginPlaces([os.path.join(os.getcwd(), 'plugins')])
            pluginManager.locatePlugins()
            pluginManager.loadPlugins()
            locationsList = []
            for target in self.project.selectedTargets:
                pluginObject = pluginManager.getPluginByName(target['pluginName'], 'Input').plugin_object
                for pl in self.project.enabledPlugins:
                    if pl['pluginName'] == target['pluginName']:
                        runtimeConfig = pl['searchOptions'] 
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
            self.emit(SIGNAL('locations(PyQt_PyObject)'), self.project)

    def __init__(self, parent=None):
        self.version = "1.1"
        QWidget.__init__(self, parent)
        self.ui = Ui_CreepyMainWindow()
        self.ui.setupUi(self)
        #Create folders for projects and temp if they do not exist
        if not os.path.exists(os.path.join(os.getcwd(),'projects')):
            os.makedirs(os.path.join(os.getcwd(),'projects'))
        if not os.path.exists(os.path.join(os.getcwd(),'temp')):
            os.makedirs(os.path.join(os.getcwd(),'temp'))
        self.projectsList = []
        self.currentProject = None
        self.ui.webPage = QWebPage()
        self.ui.webPage.mainFrame().setUrl(QUrl(os.path.join(os.getcwd(), 'include', 'map.html')))
        self.ui.mapWebView.setPage(self.ui.webPage)
        self.ui.menuView.addAction(self.ui.dockWProjects.toggleViewAction())
        self.ui.menuView.addAction(self.ui.dockWLocationsList.toggleViewAction())
        self.ui.menuView.addAction(self.ui.dockWCurrentLocationDetails.toggleViewAction())
        self.ui.actionPluginsConfiguration.triggered.connect(self.showPluginsConfigurationDialog)
        self.ui.actionNewPersonProject.triggered.connect(self.showPersonProjectWizard)
        self.ui.actionAnalyzeCurrentProject.triggered.connect(self.analyzeProject)
        self.ui.actionReanalyzeCurrentProject.triggered.connect(self.analyzeProject)
        self.ui.actionDrawCurrentProject.triggered.connect(self.presentLocations)
        self.ui.actionExportCSV.triggered.connect(self.exportProjectCSV)
        self.ui.actionExportKML.triggered.connect(self.exportProjectKML)
        self.ui.actionExportFilteredCSV.triggered.connect(functools.partial(self.exportProjectCSV, filtering=True))
        self.ui.actionExportFilteredKML.triggered.connect(functools.partial(self.exportProjectKML, filtering=True))
        self.ui.actionDeleteCurrentProject.triggered.connect(self.deleteCurrentProject)
        self.ui.actionFilterLocationsDate.triggered.connect(self.showFilterLocationsDateDialog)
        self.ui.actionFilterLocationsPosition.triggered.connect(self.showFilterLocationsPointDialog)
        self.ui.actionRemoveFilters.triggered.connect(self.removeAllFilters)
        self.ui.actionShowHeatMap.toggled.connect(self.toggleHeatMap)
        self.ui.actionReportProblem.triggered.connect(GeneralUtilities.reportProblem)
        self.ui.actionAbout.triggered.connect(self.showAboutDialog)
        self.ui.actionCheckUpdates.triggered.connect(self.checkForUpdatedVersion)
        self.ui.actionExit.triggered.connect(self.close)
        self.loadProjectsFromStorage()
        #If option enabled check for updated version

    def checkForUpdatedVersion(self):
        '''
        Checks www.geocreepy.com for an updated version and returns a tuple with the 
        result and the latest version number
        
        '''
        
        try:
            latestVersion = urllib2.urlopen("http://www.geocreepy.com/version.html").read().rstrip()
            
            updateCheckDialog = UpdateCheckDialog()
            updateCheckDialog.ui.versionsTableWidget.setHorizontalHeaderLabels(('','Component','Status','Installed','Available'))
            updateCheckDialog.ui.versionsTableWidget.setItem(0,1,QTableWidgetItem('Creepy'))
            if StrictVersion(latestVersion) > StrictVersion(self.version):
                updateCheckDialog.ui.versionsTableWidget.setItem(0,0,QTableWidgetItem(QIcon(QPixmap(':/creepy/exclamation')), ''))
                updateCheckDialog.ui.versionsTableWidget.setItem(0,2,QTableWidgetItem('Outdated'))
                updateCheckDialog.ui.dlNewVersionLabel.setText('<html><head/><body><p>Download the latest version from <a href="http://www.geocreepy.com"><span style=" text-decoration: underline; color:#0000ff;">geocreepy.com</span></a></p></body></html>')
            else:
                updateCheckDialog.ui.versionsTableWidget.setItem(0,0,QTableWidgetItem(QIcon(QPixmap(':/creepy/tick')), ''))
                updateCheckDialog.ui.versionsTableWidget.setItem(0,2,QTableWidgetItem('Up To Date'))
                updateCheckDialog.ui.dlNewVersionLabel.setText('<html><head/><body><p>You are already using the latest version of creepy. </p></body></html>')
            updateCheckDialog.ui.versionsTableWidget.setItem(0,3,QTableWidgetItem(self.version))
            updateCheckDialog.ui.versionsTableWidget.setItem(0,4,QTableWidgetItem(latestVersion))
            updateCheckDialog.show()
            updateCheckDialog.exec_()
        except Exception,err:
            if type(err) == 'string':
                mes = err
            else:
                mess = err.message
            self.showWarning(self.trUtf8('Error checking for updates'), mess)
        
    def showFilterLocationsPointDialog(self):
        filterLocationsPointDialog = FilterLocationsPointDialog()
        filterLocationsPointDialog.ui.mapPage = QWebPage()
        myPyObj = filterLocationsPointDialog.pyObj()
        filterLocationsPointDialog.ui.mapPage.mainFrame().addToJavaScriptWindowObject('myPyObj', myPyObj)  
        filterLocationsPointDialog.ui.mapPage.mainFrame().setUrl(QUrl(os.path.join(os.getcwd(), 'include', 'mapSetPoint.html')))
        filterLocationsPointDialog.ui.radiusUnitComboBox.insertItem(0, QString('km'))
        filterLocationsPointDialog.ui.radiusUnitComboBox.insertItem(1, QString('m'))
        filterLocationsPointDialog.ui.radiusUnitComboBox.activated[str].connect(filterLocationsPointDialog.onUnitChanged)
        filterLocationsPointDialog.ui.webView.setPage(filterLocationsPointDialog.ui.mapPage)
        filterLocationsPointDialog.show()
        if filterLocationsPointDialog.exec_():
            r = filterLocationsPointDialog.ui.radiusSpinBox.value()
            if filterLocationsPointDialog.unit == 'km':
                radius = r * 1000
            else:
                radius = r
            if hasattr(myPyObj, 'lat') and hasattr(myPyObj, 'lng') and radius:
                self.filterLocationsByPoint(myPyObj.lat, myPyObj.lng, radius)

    def showFilterLocationsDateDialog(self):
        filterLocationsDateDialog = FilterLocationsDateDialog()
        filterLocationsDateDialog.ui.endDateCalendarWidget.setMaximumDate(QDate.currentDate())
        filterLocationsDateDialog.show()
        if filterLocationsDateDialog.exec_():
            startDateTime = QDateTime(filterLocationsDateDialog.ui.stardateCalendarWidget.selectedDate(), filterLocationsDateDialog.ui.startDateTimeEdit.time()).toPyDateTime()
            endDateTime = QDateTime(filterLocationsDateDialog.ui.endDateCalendarWidget.selectedDate(), filterLocationsDateDialog.ui.endDateTimeEdit.time()).toPyDateTime()
            if startDateTime > endDateTime:
                self.showWarning(self.trUtf8('Invalid Dates'), self.trUtf8('The start date needs to be before the end date.<p> Please try again ! </p>'))
            else:
                self.filterLocationsByDate(startDateTime, endDateTime)
            
    def filterLocationsByDate(self, startDate, endDate):
        if not self.currentProject:
            self.showWarning(self.trUtf8('No project selected'), self.trUtf8('Please select a project !'))
            self.ui.statusbar.showMessage(self.trUtf8('Please select a project !'))
            return
        for l in self.currentProject.locations:
            if l.datetime > startDate and l.datetime < endDate:
                l.visible = True
            else:
                l.visible = False
        self.presentLocations([])
    
    def filterLocationsByPoint(self, lat, lng, radius):
        if not self.currentProject:
            self.showWarning(self.trUtf8('No project selected'), self.trUtf8('Please select a project !'))
            self.ui.statusbar.showMessage(self.trUtf8('Please select a project !'))
            return
        for l in self.currentProject.locations:
            if GeneralUtilities.calcDistance(float(lat), float(lng), float(l.latitude), float(l.longitude)) > radius:
                l.visible = False
        self.presentLocations([])

    def removeAllFilters(self):
        if not self.currentProject:
            self.showWarning(self.trUtf8('No project selected'), self.trUtf8('Please select a project !'))
            self.ui.statusbar.showMessage(self.trUtf8('Please select a project !'))
            return
        for l in self.currentProject.locations:
            l.visible = True
        self.presentLocations([])

    def showAboutDialog(self):
        aboutDialog = AboutDialog()
        aboutDialog.show()
        if aboutDialog.exec_():
            pass

    def showWarning(self, title, text):
        QMessageBox.warning(self, title, text)

    def toggleHeatMap(self, checked):
        mapFrame = self.ui.webPage.mainFrame()
        if checked:
            mapFrame.evaluateJavaScript('showHeatmap()')
            mapFrame.evaluateJavaScript('hideMarkers()')
        else:
            mapFrame.evaluateJavaScript('showMarkers()')
            mapFrame.evaluateJavaScript('hideHeatmap()')

    def hideMarkers(self):
        mapFrame = self.ui.webPage.mainFrame()
        mapFrame.evaluateJavaScript('hideMarkers()')

    def showMarkers(self):
        mapFrame = self.ui.webPage.mainFrame()
        mapFrame.evaluateJavaScript('showMarkers()')

    def addMarkerToMap(self, mapFrame, location):
        mapFrame.evaluateJavaScript(QString('addMarker(' + str(location.latitude) + ',' + str(location.longitude) + ',\"' + location.infowindow + '\")'))

    def centerMap(self, mapFrame, location):
        mapFrame.evaluateJavaScript(QString('centerMap(' + str(location.latitude) + ',' + str(location.longitude) + ')'))

    def setMapZoom(self, mapFrame, level):
        mapFrame.evaluateJavaScript(QString('setZoom(' + str(level) + ')'))

    def clearMarkers(self, mapFrame):
        mapFrame.evaluateJavaScript(QString('clearMarkers()'))

    def deleteCurrentProject(self, project):
        if not project:
            project = self.currentProject
        if project.isAnalysisRunning:
            self.showWarning(self.trUtf8('Cannot Edit Project'), self.trUtf8('Please wait until analysis is finished before performing further actions on the project'))
            return
        projectName = project.projectName+'.db'
        verifyDeleteDialog = VerifyDeleteDialog()
        verifyDeleteDialog.ui.label.setText(unicode(verifyDeleteDialog.ui.label.text(),'utf-8').replace('@project@', project.projectName))
        verifyDeleteDialog.show()
        if verifyDeleteDialog.exec_():
            project.deleteProject(projectName)
            self.loadProjectsFromStorage()
            
    def exportProjectCSV(self, project,filtering=False):
        # If the project was not provided explicitly, analyze the currently selected one
        if not project:
            project = self.currentProject
        if not project:
            self.showWarning(self.trUtf8('No project selected'), self.trUtf8('Please select a project first'))
            self.ui.statusbar.showMessage(self.trUtf8('Please select a project first'))
            return
        if not project.locations:
            self.showWarning(self.trUtf8('No locations found'), self.trUtf8('The selected project has no locations to be exported'))
            self.ui.statusbar.showMessage(self.trUtf8('The selected project has no locations to be exported'))
            return
        fileName = QFileDialog.getSaveFileName(None, self.trUtf8('Save CSV export as...'), os.getcwd(), 'All files (*.*)')
        if fileName:
            try:
                fileobj = open(fileName, 'wb')
                writer = csv.writer(fileobj, quoting=csv.QUOTE_ALL)
                writer.writerow(('Timestamp', 'Latitude', 'Longitude', 'Location Name', 'Retrieved from', 'Context'))
                for loc in project.locations:
                    if (filtering and loc.visible) or not filtering:
                        #handle unicode now that we are writing to a file                            
                        if isinstance(loc.context,unicode):
                            try:
                                writer.writerow((loc.datetime.strftime('%Y-%m-%d %H:%M:%S %z'), loc.latitude, loc.longitude,loc.shortName.encode('utf-8'), loc.plugin, loc.context.encode('utf-8')))
                            except Exception,err:
                                logger.error(err)
                                writer.writerow((loc.datetime.strftime('%Y-%m-%d %H:%M:%S %z'), loc.latitude, loc.longitude,'Non printable characters in string', loc.plugin, 'Non printable characters in string'))
                        else:
                            writer.writerow((loc.datetime.strftime('%Y-%m-%d %H:%M:%S %z'), loc.latitude, loc.longitude,loc.shortName, loc.plugin, loc.context))                 
                fileobj.close()
                self.ui.statusbar.showMessage(self.trUtf8('Project Locations have been exported successfully'))
            except Exception, err:
                logger.error(err)
                self.ui.statusbar.showMessage(self.trUtf8('Error saving the export.'))

    def exportProjectKML(self, project, filtering=False):
        # If the project was not provided explicitly, analyze the currently selected one
        if not project:
            project = self.currentProject
        if not project:
            self.showWarning(self.trUtf8('No project selected'), self.trUtf8('Please select a project first'))
            self.ui.statusbar.showMessage(self.trUtf8('Please select a project first'))
            return
        if not project.locations:
            self.showWarning(self.trUtf8('No locations found'), self.trUtf8('The selected project has no locations to be exported'))
            self.ui.statusbar.showMessage(self.trUtf8('The selected project has no locations to be exported'))
            return
        
        fileName = QFileDialog.getSaveFileName(None, self.trUtf8('Save KML export as...'), os.getcwd(), 'All files (*.*)')
        if fileName:
            try:
                fileobj = open(fileName, 'wb')
                # kml is the list to hold all xml attribs. it will be joined in a string later
                kml = []
                kml.append('<?xml version=\"1.0\" encoding=\"UTF-8\"?>')
                kml.append('<kml xmlns=\"http://www.opengis.net/kml/2.2\">') 
                kml.append('<Document>')
                kml.append('  <name>%s.kml</name>' % id)
                for loc in project.locations:
                    if (filtering and loc.visible) or not filtering:
                        #handle unicode now that we are writing to a file
                        kml.append('  <Placemark>')
                        kml.append('  <name>%s</name>' % loc.datetime.strftime('%Y-%m-%d %H:%M:%S %z'))
                        #handle unicode now that we are writing to a file                            
                        if isinstance(loc.context,unicode):
                            try:
                                kml.append('    <description> %s' % GeneralUtilities.html_escape(loc.context.encode('utf-8')))
                            except Exception, err:
                                logger.error(err)
                                kml.append('    <description> non printable characters in context')
                        else:
                            kml.append('    <description> %s' % GeneralUtilities.html_escape(loc.context))
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
                self.ui.statusbar.showMessage(self.trUtf8('Project Locations have been exported successfully'))
            except Exception, err:
                logger.error(err)
                self.ui.statusbar.showMessage(self.trUtf8('Error saving the export.'))

    def analyzeProject(self, project):
        '''
        This is called when the user clicks on "Analyze Target". It starts the background thread that
        analyzes targets and returns locations
        '''
        # If the project was not provided explicitly, analyze the currently selected one
        if not project:
            project = self.currentProject
        if project:
            if project.isAnalysisRunning:
                self.showWarning(self.trUtf8('Cannot Edit Project'), self.trUtf8('Please wait until analysis is finished before performing further actions on the project'))
                return
            self.ui.statusbar.showMessage(self.trUtf8('Analyzing project for locations. Please wait...'))
            project.isAnalysisRunning = True
            self.analyzeProjectThreadInstance = self.analyzeProjectThread(project)
            self.connect(self.analyzeProjectThreadInstance, SIGNAL('locations(PyQt_PyObject)'), self.projectAnalysisFinished)
            self.analyzeProjectThreadInstance.start()
        else:
            self.showWarning(self.trUtf8('No project selected'), self.trUtf8('Please select a project !'))
            
    def projectAnalysisFinished(self, project):
        '''
        Called when the analysis thread finishes. It saves the project with the locations and draws the map
        '''
        self.ui.statusbar.showMessage(self.trUtf8('Project Analysis complete !'))
        projectNode = ProjectNode(project.projectName, project)
        locationsNode = LocationsNode(self.trUtf8('Locations'), projectNode)
#        analysisNode = AnalysisNode(self.trUtf8('Analysis'), projectNode)
        project.isAnalysisRunning = False
        project.storeProject(projectNode)
        '''
        If the analysis produced no results whatsoever, inform the user
        '''
        if not project.locations:
            self.showWarning(self.trUtf8('No Locations Found'), self.trUtf8('We could not find any locations for the analyzed project'))
        else:
            self.presentLocations(project.locations)

    def presentLocations(self, locations):
        '''
        Also called when the user clicks on "Analyze Target". It redraws the map and populates the location list
        '''
        if not locations:
            if not self.currentProject:
                self.showWarning(self.trUtf8('No project selected'), self.trUtf8('Please select a project !'))
                self.ui.statusbar.showMessage(self.trUtf8('Please select a project !'))
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
            self.showWarning(self.trUtf8('No locations found'), self.trUtf8('No locations found for the selected project.'))
            self.ui.statusbar.showMessage(self.trUtf8('No locations found for the selected project.'))
        
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
        '''
        Called when the user clicks on a location from the location list. It updates the information 
        displayed on the Current Target Details Window
        '''
        location = self.locationsTableModel.locations[index.row()]
        self.ui.currentTargetDetailsLocationValue.setText(location.shortName)
        self.ui.currentTargetDetailsDateValue.setText(location.datetime.strftime('%Y-%m-%d %H:%M:%S %z'))
        self.ui.currentTargetDetailsSourceValue.setText(location.plugin)
        self.ui.currentTargetDetailsContextValue.setText(location.context)

    def changeMainWidgetPage(self, pageType):
        '''
        Changes what is shown in the main window between the map mode and the analysis mode
        '''
        if pageType == 'map':
            self.ui.centralStackedWidget.setCurrentIndex(0)
        else:
            self.ui.centralStackedWidget.setCurrentIndex(1)

    def wizardButtonPressed(self, plugin):
        '''
        This metod calls the wizard of the selected plugin and then reads again the configuration options from file
        for that specific plugin. This happens in order to reflect any changes the wizard might have made to the configuration 
        options.
        '''    
        plugin.plugin_object.runConfigWizard()
        self.pluginsConfigurationDialog.close()
        self.showPluginsConfigurationDialog()

    def showPluginsConfigurationDialog(self):
        '''
        Reads the configuration options for all the plugins, builds the relevant UI items and adds them to the dialog
        '''
        # Show the stackWidget
        self.pluginsConfigurationDialog = PluginsConfigurationDialog()
        self.pluginsConfigurationDialog.ui.ConfigurationDetails = QStackedWidget(self.pluginsConfigurationDialog)
        self.pluginsConfigurationDialog.ui.ConfigurationDetails.setGeometry(QRect(260, 10, 511, 561))
        self.pluginsConfigurationDialog.ui.ConfigurationDetails.setObjectName(_fromUtf8('ConfigurationDetails'))
        pl = []
        for plugin in sorted(self.pluginsConfigurationDialog.PluginManager.getAllPlugins(), key=lambda x: x.name):
            pl.append(plugin)
            '''
            Build the configuration page from the available configuration options
            and add the page to the stackwidget
            '''
            page = QWidget()
            page.setObjectName(_fromUtf8('page_' + plugin.name))
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            layout = QVBoxLayout()
            titleLabel = QLabel(plugin.name + self.trUtf8(' Configuration Options'))
            layout.addWidget(titleLabel)    
            vboxWidget = QWidget()
            vboxWidget.setObjectName(_fromUtf8('vboxwidget_container_' + plugin.name))
            vbox = QGridLayout()
            vbox.setObjectName(_fromUtf8('vbox_container_' + plugin.name))
            gridLayoutRowIndex = 0
            '''
            Load the String options first
            '''
            pluginStringOptions = plugin.plugin_object.readConfiguration('string_options')[1]
            if pluginStringOptions != None:
                for idx, item in enumerate(pluginStringOptions.keys()):
                    itemLabel = plugin.plugin_object.getLabelForKey(item)
                    label = QLabel()
                    label.setObjectName(_fromUtf8('string_label_' + item))
                    label.setText(itemLabel)
                    vbox.addWidget(label, idx, 0)
                    value = QLineEdit()
                    if item.startswith('hidden_'):
                        value.setEchoMode(QLineEdit.Password)
                    value.setObjectName(_fromUtf8('string_value_' + item))
                    value.setText(pluginStringOptions[item])
                    vbox.addWidget(value, idx, 1)
                    gridLayoutRowIndex = idx + 1
            '''
            Load the boolean options 
            '''
            pluginBooleanOptions = plugin.plugin_object.readConfiguration('boolean_options')[1]
            if pluginBooleanOptions != None:
                for idx, item in enumerate(pluginBooleanOptions.keys()):
                    itemLabel = plugin.plugin_object.getLabelForKey(item)
                    cb = QCheckBox(itemLabel)
                    cb.setObjectName(_fromUtf8('boolean_label_' + item))
                    if pluginBooleanOptions[item] == 'True':
                        cb.toggle()
                    vbox.addWidget(cb, gridLayoutRowIndex + idx, 0)
                    gridLayoutRowIndex += 1
            '''
            Add the wizard button if the plugin has a configuration wizard
            '''
            if plugin.plugin_object.hasWizard:  
                wizardButton = QPushButton(self.trUtf8('Run Configuration Wizard'))
                wizardButton.setObjectName(_fromUtf8('wizardButton_' + plugin.name))
                wizardButton.setToolTip(self.trUtf8('Click here to run the configuration wizard for the plugin'))
                wizardButton.resize(wizardButton.sizeHint())
                wizardButton.clicked.connect(functools.partial(self.wizardButtonPressed, plugin))
                vbox.addWidget(wizardButton, gridLayoutRowIndex + 1, 0)
            vboxWidget.setLayout(vbox)
            scroll.setWidget(vboxWidget)
            layout.addWidget(scroll)
            layout.addStretch(1)
            pluginsConfigButtonContainer = QHBoxLayout()
            checkConfigButton = QPushButton(self.trUtf8('Test Plugin Configuration')) 
            checkConfigButton.setObjectName(_fromUtf8('checkConfigButton_' + plugin.name))
            checkConfigButton.setToolTip(self.trUtf8('Click here to test the plugin\'s configuration'))
            checkConfigButton.resize(checkConfigButton.sizeHint())
            checkConfigButton.clicked.connect(functools.partial(self.pluginsConfigurationDialog.checkPluginConfiguration, plugin))
            applyConfigButton = QPushButton(self.trUtf8('Apply Configuration'))
            applyConfigButton.setObjectName(_fromUtf8('applyConfigButton_' + plugin.name))
            applyConfigButton.setToolTip(self.trUtf8('Click here to save the plugin\'s configuration options'))
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
        '''
        Changes the page in the PluginConfiguration Dialog depending on which plugin is currently
        selected in the plugin list
        '''
        self.pluginsConfigurationDialog.ui.ConfigurationDetails.setCurrentIndex(modelIndex.row())   

    def showPersonProjectWizard(self):
        '''
        Shows the PersonProjectWizard and stores the project information once the wizard is completed
        '''
        personProjectWizard = PersonProjectWizard()
        personProjectWizard.ProjectWizardPluginListModel = ProjectWizardPluginListModel(personProjectWizard.loadConfiguredPlugins(), self)
        personProjectWizard.ui.personProjectAvailablePluginsListView.setModel(personProjectWizard.ProjectWizardPluginListModel)
        personProjectWizard.ui.personProjectSearchButton.clicked.connect(personProjectWizard.searchForTargets)
        # Creating it here so it becomes available globally in all functions
        personProjectWizard.ProjectWizardSelectedTargetsTable = ProjectWizardSelectedTargetsTable([], self)
        if personProjectWizard.exec_():
            project = Project()
            project.projectName = unicode(personProjectWizard.ui.personProjectNameValue.text().toUtf8(), 'utf-8')
            project.projectKeywords = [keyword.strip() for keyword in unicode(personProjectWizard.ui.personProjectKeywordsValue.text().toUtf8(), 'utf-8').split(',')]
            project.projectDescription = personProjectWizard.ui.personProjectDescriptionValue.toPlainText()
            project.enabledPlugins = personProjectWizard.readSearchConfiguration()
            project.dateCreated = datetime.datetime.now()
            project.dateEdited = datetime.datetime.now()
            project.locations = []
            project.analysis = None
            project.isAnalysisRunning = False
            project.viewSettigns = {}
            project.selectedTargets = personProjectWizard.selectedTargets
            projectNode = ProjectNode(project.projectName, project)
            locationsNode = LocationsNode('Locations', projectNode)
#            analysisNode = AnalysisNode('Analysis', projectNode)
            project.storeProject(projectNode)
            # Now that we have saved the project, reload all projects to be shown in the UI
            self.loadProjectsFromStorage()

    def loadProjectsFromStorage(self):
        """
        Loads all the existing projects from the storage to be shown in the UI
        """
        # Show the existing Projects 
        projectsDir = os.path.join(os.getcwd(), 'projects')
        projectFileNames = [ os.path.join(projectsDir, f) for f in os.listdir(projectsDir) if (os.path.isfile(os.path.join(projectsDir, f)) and f.endswith('.db'))]
        rootNode = ProjectTreeNode(self.trUtf8('Projects'))
        for projectFile in projectFileNames:
            projectObject = shelve.open(projectFile)
            try:
                rootNode.addChild(projectObject['project'])
            except Exception, err:
                logger.error('Could not read stored project from file')
                logger.exception(err)
        self.projectTreeModel = ProjectTreeModel(rootNode) 
        self.ui.treeViewProjects.setModel(self.projectTreeModel)
        self.ui.treeViewProjects.doubleClicked.connect(self.doubleClickProjectItem)
        self.ui.treeViewProjects.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.treeViewProjects.customContextMenuRequested.connect(self.showRightClickMenu)
        self.ui.treeViewProjects.clicked.connect(self.currentProjectChanged)
    
    def currentProjectChanged(self, index):
        '''
        Called whenever a project node or one of its children is clicked
        and makes this the currently selected project
        '''
        nodeObject = self.ui.treeViewProjects.selectionModel().selection().indexes()[0].internalPointer()
        if nodeObject.nodeType() == 'PROJECT':
            self.currentProject = nodeObject.project
        elif nodeObject.nodeType() == 'LOCATIONS':
            self.currentProject = nodeObject.parent().project  
        elif nodeObject.nodeType() == 'ANALYSIS':
            self.currentProject = nodeObject.parent().project

    def doubleClickProjectItem(self):
        '''
        Called when the user double-clicks on an item in the tree of the existing projects
        '''
        nodeObject = self.ui.treeViewProjects.selectionModel().selection().indexes()[0].internalPointer()
        if nodeObject.nodeType() == 'PROJECT':
            self.currentProject = nodeObject.project
            self.changeMainWidgetPage('map')
            self.presentLocations([])
        elif nodeObject.nodeType() == 'LOCATIONS':
            self.currentProject = nodeObject.parent().project
            self.changeMainWidgetPage('map')
            self.presentLocations([])
        elif nodeObject.nodeType() == 'ANALYSIS':
            self.currentProject = nodeObject.parent().project
            self.changeMainWidgetPage('analysis')
        
    def showRightClickMenu(self, pos):
        '''
        Called when the user right-clicks somewhere in the area of the existing projects
        '''
        # We will not allow multi select so the selectionModel().selection().indexes() will contain only one
        if self.ui.treeViewProjects.selectionModel().selection().count() == 1:
            nodeObject = self.ui.treeViewProjects.selectionModel().selection().indexes()[0].internalPointer()
            if nodeObject.nodeType() == 'PROJECT':
                # First make this the current project
                self.currentProject = nodeObject.project
                #now depending on if the project is analyzed or not add actions to the menu
                rightClickMenu = QMenu()
                if nodeObject.project.locations:
                    rightClickMenu.addAction(self.ui.actionReanalyzeCurrentProject)
                    rightClickMenu.addAction(self.ui.actionDrawCurrentProject)
                    rightClickMenu.addAction(self.ui.actionDeleteCurrentProject)
                    rightClickMenu.addAction(self.ui.actionExportCSV)
                    rightClickMenu.addAction(self.ui.actionExportKML)
                    rightClickMenu.addAction(self.ui.actionExportFilteredCSV)
                    rightClickMenu.addAction(self.ui.actionExportFilteredKML)
                else:
                    rightClickMenu.addAction(self.ui.actionAnalyzeCurrentProject)
                    rightClickMenu.addAction(self.ui.actionDeleteCurrentProject)
                    
                if rightClickMenu.exec_(self.ui.treeViewProjects.viewport().mapToGlobal(pos)):
                    pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())

