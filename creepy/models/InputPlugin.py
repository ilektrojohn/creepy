#!/usr/bin/python
# -*- coding: utf-8 -*-
from yapsy.IPlugin import IPlugin
from configobj import ConfigObj
import logging
import os
from os.path import expanduser
from utilities import GeneralUtilities

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(os.path.join(GeneralUtilities.getLogDir(), 'creepy_main.log'))
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


class MultiLevelConfigObj(ConfigObj):
    """
Behaves like configobj.ConfigObj to the API users, but will load
settings from several files in a priority list (think
/usr/share/configfile, /etc/configfile, ~/.configfile), and only write
settings different from the values in the previous configuration files
into the last configuration file, which is expected to be writable.

This is implemented by having one memory backed ConfigObj populated
with information loaded from the files, and checking the files for
content when saving.

"""

    def __init__(self, infiles=[]):
        super(MultiLevelConfigObj, self).__init__(infile=None)
        self.backing = []
        for infile in infiles:
            config = ConfigObj(infile=infile)
            self.backing.append(config)
            for section in config.keys():
                if section not in self:
                    self[section] = {}
                for key in config[section].keys():
                    self[section][key] = config[section][key]

    def write(self, outfile=None, section=None):
        changed = False
        if outfile is None:
            writebackend = self.backing[len(self.backing) - 1]
        else:
            writebackend = ConfigObj(infile=outfile)
        if section is None:
            sections = self.sections
        else:
            sections = section
        for section in sections:
            for key in self[section].keys():
                saveval = None
                for backend in self.backing:
                    if section in backend and key in backend[section]:
                        saveval = backend[section][key]
                if self[section][key] != saveval:
                    if section not in writebackend:
                        writebackend[section] = {}
                    writebackend[section][key] = self[section][key]
                    changed = True
        if changed:
            logger.debug('writing ini file ')
            return writebackend.write()
        else:
            logger.debug('not writing ini file ')
            # Nothing changed from the files on disk, no need to write anything.

    @staticmethod
    def testclass():
        """
Self test assuming these files exist:

***** foo.ini *****
[foosection]
foo=value

[section]
key=foovalue
***** bar.ini *****
[barsection]
bar=value

[section]
key=barvalue

"""
        infiles = ['foo.ini', 'bar.ini', 'user.ini']
        config = MultiLevelConfigObj(infiles=infiles)
        if 'section' not in config:
            print('error: section missing from config')
        config['section'] = {}
        config['section']['key'] = 'floffa'
        config['foosection']['foo'] = 'replaced'
        config['foosection']['foo'] = 'value'
        config.write()
        print(config)


class InputPlugin(IPlugin):

    name = 'Plugin_Name'

    def __init__(self):
        pass

    def activate(self):
        pass

    def hasLocationBasedMode(self):
        return False

    def deactivate(self):
        pass

    def searchForTargets(self, search_term):
        return 'dummyUser'

    def loadConfiguration(self):
        pass

    def isConfigured(self):
        return True, ''

    def returnLocations(self, target, search_params):
        pass

    def returnPersonalInformation(self, search_params):
        pass

    def getConfigObj(self, config_filename=None):
        if config_filename is None:
            config_filename = self.name + '.conf'
        configfiles = []
        for directory in GeneralUtilities.getPluginDirs():
            configfiles.append(expanduser(os.path.join(directory, self.name, config_filename)))
        logger.debug('Loading config from: ' + str(configfiles))
        config = MultiLevelConfigObj(infiles=configfiles)
        config.create_empty = False
        return config

    def readConfiguration(self, category):
        if not hasattr(self, 'config'):
            self.config = self.getConfigObj()
        try:
            options = self.config[category]
        except Exception, err:
            options = None
            logger.error('Could not load the ' + category + ' for the ' + self.name + ' plugin .')
            logger.exception(err)
        return self.config, options

    def saveConfiguration(self, new_config):
        try:
            for c in ['string_options', 'boolean_options']:
                for l in self.config[c].keys():
                    if self.config[c][l] != new_config[c][l]:
                        self.config[c][l] = new_config[c][l]
            GeneralUtilities.getLocalPluginDir(self.name)
            self.config.write()
        except Exception, err:
            logger.error('Could not save the configuration for the ' + self.name + ' plugin.')
            logger.exception(err)

    def loadSearchConfigurationParameters(self):
        if not hasattr(self, 'config'):
            self.config = self.getConfigObj()
        try:
            params = self.config['search_options']
        except Exception, err:
            params = None
            logger.error('Could not load the search configuration parameters for the ' + self.name + ' plugin.')
            logger.exception(err)

        return params

    def getLabelForKey(self, key):
        """
        If the developer of the plugin has not implemented this function in the plugin, 
        return the key name to be used in the label
        """
        return key
