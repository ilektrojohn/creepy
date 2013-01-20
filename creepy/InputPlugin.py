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
        
    def loadConfiguration(self):
        pass
    
    def isFunctional(self):
        pass
    
    def returnLocations(self, search_params):
        pass
    
    def returnPersonalInformation(self, search_params):
        pass
        
    def readConfiguration(self, category):
        config_filename = self.plugin_name+".conf"
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
        return options
    def saveConfiguration(self):
        pass
        