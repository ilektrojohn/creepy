#!/usr/bin/python
# -*- coding: utf-8 -*-
import shelve
import os
import logging
from utilities import GeneralUtilities

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(os.path.join(GeneralUtilities.getLogDir(), 'creepy_main.log'))
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


class Project(object):
    def __init__(self, projectType=None, projectName=None, selectedTargets=None, projectKeywords=None,
                 projectDescription=None, enabledPlugins=None, dateCreated=None, locations=None, analysis=None,
                 analysisDocument=None,dateEdited=None, results=None, viewSettings=None, poi=None):
        self.projectType = projectType
        self.projectName = projectName
        self.selectedTargets = selectedTargets
        self.projectKeywords = projectKeywords
        self.projectDescription = projectDescription
        self.enabledPlugins = enabledPlugins
        self.dateCreated = dateCreated
        self.dateEdited = dateEdited
        self.locations = locations
        self.poi = poi
        self.analysis = analysis
        self.viewSettings = viewSettings
        self.isAnalysisRunning = False

    def storeProject(self, projectNodeObject):
        """
        Receives a projectNodeObject and stores it using the selected data persistence method.
        Decoupled here for flexibility
        """
        projectName = projectNodeObject.name().encode('utf-8') + '.db'

        storedProject = shelve.open(os.path.join(GeneralUtilities.getProjectsDir(), projectName))
        try:
            storedProject['project'] = projectNodeObject
        except Exception, err:
            logger.error('Error saving the project ')
            logger.exception(err)
        finally:
            storedProject.close()

    def deleteProject(self, projectName):
        # projectName comes as a Unicode, so we need to encode it to a string for shelve to find it
        try:
            os.remove(os.path.join(GeneralUtilities.getProjectsDir(), projectName.encode('utf-8')))
        except Exception, err:
            logger.error('Error deleting the project')
            logger.exception(err)
