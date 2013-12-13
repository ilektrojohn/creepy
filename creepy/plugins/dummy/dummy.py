from InputPlugin import InputPlugin
import datetime

class Dummy(InputPlugin):
    name = "dummy"
    configured = False
    hasWizard = False
    
    
    def __init__(self):
        pass
    def activate(self):
        pass
        
    def deactivate(self):
        pass
        
    def searchForTargets(self, search_term):
        return {'pluginName':'Dummy Plugin', 'targetUsername':'dummyusername', 'targetFullname': 'dummy fullname', 'targetPicture': '303ec0c.jpg', 'targetDetails': 'Profile description'}
    
    def loadConfiguration(self):
        pass
    
    def isFunctional(self):
        return True
    
    def returnLocations(self, target, search_params):
        d = datetime.datetime.strptime('2009-08-19 14:20:36 UTC', "%Y-%m-%d %H:%M:%S %Z")
        locations = [{'plugin': self.name,'lon':38.343242,'lat':23.3213,'context':'this is the context', 'shortName':'This is the short name','date':d},{'plugin': self.name,'lon':40.343242,'lat':29.3213,'context':'this is the context2', 'shortName':'This is the short name2', 'date':d}]
        return locations
    
    def returnPersonalInformation(self, search_params):
        pass
    
    def isConfigured(self):
        return (True,"")   
