from InputPlugin import InputPlugin

class Flickr(InputPlugin):
    
    name = "flickr"
    configured = False
    
    
    
    def __init__(self):
        pass
    def activate(self):
        pass
        
    def deactivate(self):
        pass
        
    def searchForTargets(self):
        return {'pluginName':'Flickr Plugin', 'targetUsername':'flickrusername', 'targetFullname': 'flickr fullname', 'targetPicture': '303ec0sasac.jpg', 'targetDetails': 'Flickr Profile description'}
    
    def loadConfiguration(self):
        pass
    
    def isFunctional(self):
        return True
    
    def returnLocations(self, target, search_params):
        pass
    
    def returnPersonalInformation(self, search_params):
        pass
    