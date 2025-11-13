#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtGui import QDialog, QLabel, QLineEdit, QScrollArea, QCheckBox
from yapsy.PluginManager import PluginManagerSingleton
from models.InputPlugin import InputPlugin
from ui.PluginsConfig import Ui_PluginsConfigurationDialog
from components.PluginConfigurationCheckDialog import PluginConfigurationCheckdialog
from components.PluginRatesCheckDialog import PluginRatesCheckDialog
from utilities import GeneralUtilities
from datetime import datetime


class PluginsConfigurationDialog(QDialog):
    def __init__(self, parent=None):
        # Load the installed plugins and read their metadata
        self.PluginManager = PluginManagerSingleton.get()
        self.PluginManager.setCategoriesFilter({'Input': InputPlugin})
        self.PluginManager.setPluginPlaces(GeneralUtilities.getPluginDirs())
        self.PluginManager.locatePlugins()
        self.PluginManager.collectPlugins()
        QDialog.__init__(self, parent)
        self.ui = Ui_PluginsConfigurationDialog()
        self.ui.setupUi(self)

    def getRateLimitStatus(self, plugin):
        """
        Calls the getRateLimitStatus of the selected Plugin if it supports it and provides a popup window with the result
        """
        checkPluginRatesDialog = PluginRatesCheckDialog()
        if plugin.plugin_object.hasRateLimitInfo:
            search, location, person = plugin.plugin_object.getRateLimitStatus('all')
            checkPluginRatesDialog.ui.checkPluginRatesLabel.setText(self.trUtf8(
                'You have {0} out of {1} API calls for searching users. Limit will be renewed on {2}\n'.format(
                    search['remaining'], search['limit'],
                    datetime.fromtimestamp(search['reset']).strftime('%Y-%m-%d %H:%M:%S %z')) +
                'You have {0} out of {1} API calls for analyzing place based projects. Limit will be renewed on {2}\n'.format(
                    location['remaining'], location['limit'],
                    datetime.fromtimestamp(location['reset']).strftime('%Y-%m-%d %H:%M:%S %z')) +
                'You have {0} out of {1} API calls for analyzing person based projects. Limit will be renewed on {2}\n'.format(
                    person['remaining'], person['limit'],
                    datetime.fromtimestamp(person['reset']).strftime('%Y-%m-%d %H:%M:%S %z'))
            ))
        else:
            checkPluginRatesDialog.ui.checkPluginRatesLabel.setText(
                self.trUtf8('This plugin does not support this function.'))
        checkPluginRatesDialog.exec_()

    def checkPluginConfiguration(self, plugin):
        """
        Calls the isConfigured of the selected Plugin and provides a popup window with the result
        """
        self.saveConfiguration()
        checkPluginConfigurationResultDialog = PluginConfigurationCheckdialog()
        isConfigured = plugin.plugin_object.isConfigured()
        if isConfigured[0]:
            checkPluginConfigurationResultDialog.ui.checkPluginConfigurationResultLabel.setText(
                plugin.name + self.trUtf8(' is correctly configured.') + isConfigured[1])
        else:
            checkPluginConfigurationResultDialog.ui.checkPluginConfigurationResultLabel.setText(
                plugin.name + self.trUtf8(' is not correctly configured.') + isConfigured[1])
        checkPluginConfigurationResultDialog.exec_()

    def saveConfiguration(self):
        """
        Reads all the configuration options for the plugins and calls the saveConfiguration method of all the plugins.
        """
        pages = (self.ui.ConfigurationDetails.widget(i) for i in range(self.ui.ConfigurationDetails.count()))
        for page in pages:
            for widg in [scrollarea.children() for scrollarea in page.children() if type(scrollarea) == QScrollArea]:
                for i in widg[0].children():
                    config_options = {}
                    plugin_name = i.objectName().replace('vboxwidget_container_', '')
                    string_options = {}
                    for j in i.findChildren(QLabel):
                        string_options[str(j.objectName().replace('string_label_', ''))] = str(
                            i.findChild(QLineEdit, j.objectName().replace('label', 'value')).text())
                    boolean_options = {}
                    for k in i.findChildren(QCheckBox):
                        boolean_options[str(k.objectName().replace('boolean_label_', ''))] = str(k.isChecked())

                    config_options['string_options'] = string_options
                    config_options['boolean_options'] = boolean_options
                    plugin = self.PluginManager.getPluginByName(plugin_name, 'Input')
                    if plugin:
                        plugin.plugin_object.saveConfiguration(config_options)
