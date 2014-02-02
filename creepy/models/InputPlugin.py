#!/usr/bin/python
# -*- coding: utf-8 -*-
from yapsy.IPlugin import IPlugin
from configobj import ConfigObj
import logging
import os
from utilities import GeneralUtilities

#set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(os.path.join(GeneralUtilities.getUserHome(),'creepy_main.log'))
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

class InputPlugin(IPlugin):

    def __init__(self):
        pass
    def activate(self):
        pass
        
    def deactivate(self):
        pass
    
    def searchForTargets(self, search_term):
        return 'dummyUser'
    
    def loadConfiguration(self):
        pass
    
    def isConfigured(self):
        return (True,"")
    
    def returnLocations(self, target, search_params):
        pass
    
    def returnPersonalInformation(self, search_params):
        pass
    def getConfigObj(self):    
        config_filename = self.name+".conf"
        config_file = os.path.join(os.getcwdu(),'plugins', self.name, config_filename)
        config = ConfigObj(infile=config_file)
        config.create_empty=False
    
    def readConfiguration(self, category):
        config_filename = self.name+'.conf'
        config_file = os.path.join(os.getcwdu(),'plugins', self.name, config_filename)
        config = ConfigObj(infile=config_file)
        config.create_empty=False
        try:
            options = config[category]
        except Exception,err:
            options = None 
            logger.error('Could not load the '+category+' for the '+self.name+' plugin .')
            logger.exception(err)
        return config,options

    def saveConfiguration(self, new_config):
        config_filename = self.name+'.conf'
        config_file = os.path.join(os.getcwdu(),'plugins',self.name, config_filename)
        config = ConfigObj(infile=config_file)
        config.create_empty=False
        try:
            config['string_options'] = new_config['string_options']
            config['boolean_options'] = new_config['boolean_options']
            config.write()
        except Exception, err:
            logger.error('Could not save the configuration for the '+self.name+' plugin.')
            logger.exception(err)

    def loadSearchConfigurationParameters(self):
        config_filename = self.name+'.conf'
        config_file = os.path.join(os.getcwdu(),  'plugins', self.name, config_filename)
        config = ConfigObj(infile=config_file)
        config.create_empty = False
        try:
            params = config['search_options']
        except Exception, err:
            params= None
            logger.error('Could not load the search configuration parameters for the '+self.name+' plugin.')
            logger.exception(err)
        
        return params    
            
    def getLabelForKey(self, key):
        '''
        If the developer of the plugin has not implemented this function in the plugin, 
        return the key name to be used in the label
        '''  
        return key