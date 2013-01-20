from InputPlugin import InputPlugin


class Dummy(InputPlugin):
    name = "Dummy Plugin"
    plugin_name = "dummy"
    
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
        
    
        
        
    def saveConfiguration(self):
        pass