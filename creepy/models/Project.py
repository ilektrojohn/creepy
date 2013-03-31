import datetime

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