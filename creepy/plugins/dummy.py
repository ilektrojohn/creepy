from InputPlugin import InputPlugin


class Dummy(InputPlugin):
    name = "dummy"
    configured = False
    
    
    def __init__(self):
        pass
    def activate(self):
        pass
        
    def deactivate(self):
        pass
        
    def searchForTargets(self):
        return {'targetUsername':'dummyusername', 'targetFullname': 'dummy fullname', 'targetPicture': '303ec0c.jpg', 'targetDetails': 'Profile description'}
    
    def loadConfiguration(self):
        pass
    
    def isFunctional(self):
        return True
    
    def returnLocations(self, search_params):
        pass
    
    def returnPersonalInformation(self, search_params):
        pass
        
