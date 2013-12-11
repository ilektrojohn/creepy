import datetime
import shelve
import os
import logging

class Project(object):
    def __init__(self, projectName = None, selectedTargets=None, projectKeywords = None, projectDescription = None, enabledPlugins = None,dateCreated = None, locations = None, analysis=None, dateEdited=None, results=None, viewSettings = None):
        self.projectName= projectName
        self.selectedTargets = selectedTargets
        self.projectKeywords = projectKeywords
        self.projectDescription = projectDescription
        self.enabledPlugins =enabledPlugins
        self.dateCreated = dateCreated
        self.dateEdited = dateEdited
        self.locations = locations
        self.analysis = analysis
        self.viewSettings = viewSettings
        self.isAnalysisRunning = False
        
    def storeProject(self, projectNodeObject):
        """
        Receives a projectNodeObject and stores it using the selected data persistence method. 
        Decoupled here for flexibility
        """
        projectName = projectNodeObject.name()+".db"
        
        storedProject = shelve.open(os.path.join(os.getcwd(),"projects",projectName))
        try:
            storedProject['project'] = projectNodeObject
        except Exception,err:
            logging.log(logging.ERROR, "Error saving the project ")
            logging.exception(err)
        finally:
            storedProject.close()
    
    def deleteProject(self, projectName):
        try:
            os.remove(os.path.join(os.getcwd(),"projects",projectName))
        except Exception,err:
            logging.log(logging.ERROR, "Error deleting the project ")
            logging.exception(err)