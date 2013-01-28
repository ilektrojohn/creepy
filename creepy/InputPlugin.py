from yapsy.IPlugin import IPlugin
from configobj import ConfigObj
import logging
import os
'''
Created on Jan 19, 2013

@author: ioannis
'''

class InputPlugin(IPlugin):
    '''
    classdocs
    '''

    def __init__(self):
        pass
    def activate(self):
        pass
        
    def deactivate(self):
        pass
    
    def searchForTargets(self):
        return 'dummyUser'
    
    def loadConfiguration(self):
        pass
    
    def isFunctional(self):
        pass
    
    def returnLocations(self, search_params):
        pass
    
    def returnPersonalInformation(self, search_params):
        pass
        
    def readConfiguration(self, category):
        config_filename = self.name+".conf"
        config_file = os.path.join(os.getcwd(),'creepy','plugins',config_filename)
        config = ConfigObj(infile=config_file)
        config.create_empty=False
        try:
            print config
            logging.log(logging.DEBUG, "Trying to load the "+category+" for the "+self.name+" plugin .")
            options = config[category]
        except Exception,err:
            options = None 
            logging.log(logging.ERROR, "Could not load the "+category+" for the "+self.name+" plugin .")  
            logging.exception(err) 
        return options
    def saveConfiguration(self, new_config):
        config_filename = self.name+".conf"
        config_file = os.path.join(os.getcwd(),'creepy','plugins',config_filename)
        config = ConfigObj(infile=config_file)
        config.create_empty=False
        try:
            logging.log(logging.DEBUG, "Trying to save the configuration for the "+self.name+" plugin .")
            config['string_options'] = new_config['string_options']
            config['boolean_options'] = new_config['boolean_options']
            config.write()
        except Exception, err:
            logging.error("Could not save the configuration for the "+self.name+" plugin .")
            logging.exception(err)
        