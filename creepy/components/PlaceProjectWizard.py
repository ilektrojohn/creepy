#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtGui import QWizard, QMessageBox, QWidget, QScrollArea, QLineEdit, QLabel, QVBoxLayout, QCheckBox, \
    QGridLayout
from PyQt4.QtCore import QObject, pyqtSlot, QString
from models.PluginConfigurationListModel import PluginConfigurationListModel
from models.InputPlugin import InputPlugin
from yapsy.PluginManager import PluginManagerSingleton
from ui.PlaceProjectWizard import Ui_placeProjectWizard
from utilities import GeneralUtilities

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class PlaceProjectWizard(QWizard):
    """ Loads the Place Based Project Wizard from the ui and shows it """

    def __init__(self, parent=None):
        QWizard.__init__(self, parent)
        self.ui = Ui_placeProjectWizard()
        self.ui.setupUi(self)
        self.enabledPlugins = []
        self.selectedPlugins = []
        self.PluginManager = None
        self.SearchConfigPluginConfigurationListModel = None
        # Register the project name field so that it will become mandatory
        self.page(0).registerField('name*', self.ui.placeProjectNameValue)
        self.unit = 'km'
        self.myPyObj = self.PyObj()

    class PyObj(QObject):
        def __init__(self):
            QObject.__init__(self)
            self.poi_marked = False
            self.lat = None
            self.lng = None

        @pyqtSlot(str)
        def setLatLng(self, latlng):
            self.poi_marked = True
            lat, lng = latlng.replace('(', '').replace(')', '').split(',')
            self.lat = float(lat)
            self.lng = float(lng)

    def showWarning(self, title, text):
        QMessageBox.warning(self, title, text, None)

    def validateCurrentPage(self):
        if self.currentPage() == self.ui.placeProjectWizardPage2:
            if not self.myPyObj.poi_marked:
                self.showWarning('No POI selected',
                                 'Please select a Point of interest before proceeding.')
            return self.myPyObj.poi_marked
        else:
            return super(PlaceProjectWizard, self).validateCurrentPage()

    def initializePage(self, i):
        """
        If the page to be loaded is the page containing the search
        options for our plugins, store the selected targets and load the relative search options based on the
        selected target.
        """
        if i == 3:
            self.selectedPlugins = list(self.ProjectWizardPluginListModel.checkedPlugins)
            self.showPluginsSearchOptions()

    def onUnitChanged(self, index):
        self.unit = index

    def loadConfiguredPlugins(self):
        """
        Returns a list with the configured plugins that can be used for place based projects
        """
        self.PluginManager = PluginManagerSingleton.get()
        self.PluginManager.setCategoriesFilter({'Input': InputPlugin})
        self.PluginManager.setPluginPlaces(GeneralUtilities.getPluginDirs())
        self.PluginManager.locatePlugins()
        self.PluginManager.loadPlugins()
        pluginList = sorted(self.PluginManager.getAllPlugins(), key=lambda x: x.name)
        return [[plugin, 0] for plugin in pluginList if plugin.plugin_object.hasLocationBasedMode is True]

    def showPluginsSearchOptions(self):
        """
        Loads the search options of all the selected plugins and populates the relevant UI elements
        with input fields for the string options and checkboxes for the boolean options
        """
        pl = []
        for pluginName in self.selectedPlugins:
            plugin = self.PluginManager.getPluginByName(pluginName, 'Input')
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
        self.ui.placeProjectWizardSearchConfigPluginsList.setModel(self.SearchConfigPluginConfigurationListModel)
        self.ui.placeProjectWizardSearchConfigPluginsList.clicked.connect(self.changePluginConfigurationPage)

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
