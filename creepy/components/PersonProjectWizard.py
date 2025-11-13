#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4.QtGui import QWizard, QMessageBox, QWidget, QScrollArea, QLineEdit, QLabel, QVBoxLayout, QCheckBox, \
    QGridLayout
from PyQt4.QtCore import QString
from models.PluginConfigurationListModel import PluginConfigurationListModel
from models.ProjectWizardPossibleTargetsTable import ProjectWizardPossibleTargetsTable
from models.InputPlugin import InputPlugin
from yapsy.PluginManager import PluginManagerSingleton
from ui.PersonProjectWizard import Ui_personProjectWizard
from utilities import GeneralUtilities

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class PersonProjectWizard(QWizard):
    """ Loads the Person Based Project Wizard from the ui and shows it """

    def __init__(self, parent=None):
        QWizard.__init__(self, parent)
        self.ui = Ui_personProjectWizard()
        self.ui.setupUi(self)
        self.selectedTargets = []
        self.enabledPlugins = []
        self.ProjectWizardPossibleTargetsTable = None
        self.PluginManager = None
        self.SearchConfigPluginConfigurationListModel = None
        # Register the project name field so that it will become mandatory
        self.page(0).registerField('name*', self.ui.personProjectNameValue)

        self.ui.btnAddTarget.clicked.connect(self.addTargetsToSelected)
        self.ui.btnRemoveTarget.clicked.connect(self.removeTargetsFromSelected)
        self.ui.personProjectSearchForValue.returnPressed.connect(self.ui.personProjectSearchButton.setFocus)

    def addTargetsToSelected(self):
        selected = self.ui.personProjectSearchResultsTable.selectionModel().selectedRows()
        newTargets = [self.ui.personProjectSearchResultsTable.model().targets[i.row()] for i in selected]
        self.ui.personProjectSelectedTargetsTable.model().insertRows(newTargets, len(newTargets))

    def removeTargetsFromSelected(self):
        selected = self.ui.personProjectSelectedTargetsTable.selectionModel().selectedRows()
        toRemove = [self.ui.personProjectSelectedTargetsTable.model().targets[i.row()] for i in selected]
        self.ui.personProjectSelectedTargetsTable.model().removeRows(toRemove, len(toRemove))

    def showWarning(self, title, text):
        QMessageBox.warning(self, title, text, None)

    def validateCurrentPage(self):
        """
        Validates that when clicking Next at the Target Selection page, the user has already selected a target
        """
        if self.currentPage() == self.ui.personProjectWizardPage2:
            if not self.ProjectWizardSelectedTargetsTable.targets:
                self.showWarning('No target selected',
                                 'Please drag and drop your targets to the selected targets before proceeding.')
            return bool(self.ProjectWizardSelectedTargetsTable.targets)
        else:
            return super(PersonProjectWizard, self).validateCurrentPage()

    def initializePage(self, i):
        """
        If the page to be loaded is the page containing the search
        options for our plugins, store the selected targets and load the relative search options based on the 
        selected target.
        """
        if i == 2:
            self.storeSelectedTargets()
            self.showPluginsSearchOptions()

    def checkIfSelectedTargets(self):
        if not self.ProjectWizardSelectedTargetsTable.targets:
            self.showWarning('No target selected',
                             'Please drag and drop your targets to the selected targets before proceeding')
            self.back()
            self.next()

    def storeSelectedTargets(self):
        """
        Stores a list of the selected targets for future use
        """
        self.selectedTargets = []
        for target in self.ProjectWizardSelectedTargetsTable.targets:
            self.selectedTargets.append({'pluginName': target['pluginName'],
                                         'targetUsername': target['targetUsername'],
                                         'targetUserid': target['targetUserid'],
                                         'targetFullname': target['targetFullname']
                                         })

    def searchForTargets(self):
        """
        Iterates the selected plugins and for each one performs a search with the given criteria. It
        then populates the PossibleTargets ListModel with the results
        """
        search_term = self.ui.personProjectSearchForValue.text().toUtf8()
        if not search_term:
            self.showWarning(self.trUtf8('Empty Search Term'), self.trUtf8('Please enter a search term'))
        else:
            selectedPlugins = list(self.ProjectWizardPluginListModel.checkedPlugins)
            possibleTargets = []
            for i in selectedPlugins:
                pluginTargets = self.PluginManager.getPluginByName(i, 'Input').plugin_object.searchForTargets(
                    search_term)

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
        self.PluginManager.setCategoriesFilter({'Input': InputPlugin})
        self.PluginManager.setPluginPlaces(GeneralUtilities.getPluginDirs())
        self.PluginManager.locatePlugins()
        self.PluginManager.loadPlugins()
        pluginList = sorted(self.PluginManager.getAllPlugins(), key=lambda x: x.name)
        return [[plugin, 0] for plugin in pluginList]

    def showPluginsSearchOptions(self):
        """
        Loads the search options of all the selected plugins and populates the relevant UI elements
        with input fields for the string options and checkboxes for the boolean options
        """
        pl = []
        for pluginName in list(
                set([target['pluginName'] for target in self.ProjectWizardSelectedTargetsTable.targets])):
            plugin = self.PluginManager.getPluginByName(pluginName, 'Input')
            self.enabledPlugins.append(plugin)
            pl.append(plugin)
            '''
            Build the configuration page from the available saerch options
            and add the page to the stackwidget
            '''
            page = QWidget()
            page.setObjectName(_fromUtf8('searchconfig_page_' + plugin.name))
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            layout = QVBoxLayout()
            titleLabel = QLabel(_fromUtf8(plugin.name + self.trUtf8(' Search Options')))
            layout.addWidget(titleLabel)
            vboxWidget = QWidget()
            vboxWidget.setObjectName(_fromUtf8('searchconfig_vboxwidget_container_' + plugin.name))
            vbox = QGridLayout()
            vbox.setObjectName(_fromUtf8('searchconfig_vbox_container_' + plugin.name))
            gridLayoutRowIndex = 0
            # Load the String options first
            pluginStringOptions = plugin.plugin_object.readConfiguration('search_string_options')[1]
            if pluginStringOptions:
                for idx, item in enumerate(pluginStringOptions.keys()):
                    itemLabel = plugin.plugin_object.getLabelForKey(item)
                    label = QLabel()
                    label.setObjectName(_fromUtf8('searchconfig_string_label_' + item))
                    label.setText(itemLabel)
                    vbox.addWidget(label, idx, 0)
                    value = QLineEdit()
                    value.setObjectName(_fromUtf8('searchconfig_string_value_' + item))
                    value.setText(pluginStringOptions[item])
                    vbox.addWidget(value, idx, 1)
                    gridLayoutRowIndex = idx + 1
            # Load the boolean options
            pluginBooleanOptions = plugin.plugin_object.readConfiguration('search_boolean_options')[1]
            if pluginBooleanOptions:
                for idx, item in enumerate(pluginBooleanOptions.keys()):
                    itemLabel = plugin.plugin_object.getLabelForKey(item)
                    cb = QCheckBox(itemLabel)
                    cb.setObjectName(_fromUtf8('searchconfig_boolean_label_' + item))
                    if pluginBooleanOptions[item] == 'True':
                        cb.toggle()
                    vbox.addWidget(cb, gridLayoutRowIndex + idx, 0)
            # If there are no search options just show a message
            if not pluginBooleanOptions and not pluginStringOptions:
                label = QLabel()
                label.setObjectName(_fromUtf8('no_search_config_options'))
                label.setText(self.trUtf8('This plugin does not offer any search options.'))
                vbox.addWidget(label, 0, 0)

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
        Reads all the search configuration options for the enabled plugins and and returns a list of the enabled plugins
        and their options.
        """
        enabledPlugins = []
        pages = (self.ui.searchConfiguration.widget(i) for i in range(self.ui.searchConfiguration.count()))
        for page in pages:
            for widg in [scrollarea.children() for scrollarea in page.children() if type(scrollarea) == QScrollArea]:
                for i in widg[0].children():
                    plugin_name = str(i.objectName().replace('searchconfig_vboxwidget_container_', ''))
                    string_options = {}
                    for j in i.findChildren(QLabel):
                        if str(j.text()).startswith('searchconfig'):
                            string_options[str(j.objectName().replace('searchconfig_string_label_', ''))] = str(
                                i.findChild(QLineEdit, j.objectName().replace('label', 'value')).text())
                    boolean_options = {}
                    for k in i.findChildren(QCheckBox):
                        boolean_options[str(k.objectName().replace('searchconfig_boolean_label_', ''))] = str(
                            k.isChecked())

                    enabledPlugins.append({'pluginName': plugin_name,
                                           'searchOptions': {'string': string_options, 'boolean': boolean_options}})
        return enabledPlugins
