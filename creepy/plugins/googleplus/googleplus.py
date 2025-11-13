#!/usr/bin/python
# -*- coding: utf-8 -*-
from models.InputPlugin import InputPlugin
from oauth2client.client import OAuth2WebServerFlow, AccessTokenCredentials
from googleapiclient.discovery import build
import logging
import os
import urllib
import httplib2
import dateutil.parser
from PyQt4.QtGui import QWizard, QWizardPage, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt4.QtCore import QUrl
from PyQt4.QtWebKit import QWebView
from utilities import GeneralUtilities, QtHandler
# set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(os.path.join(GeneralUtilities.getLogDir(), 'creepy_main.log'))
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s:%(asctime)s  In %(filename)s:%(lineno)d: %(message)s')
fh.setFormatter(formatter)
guiLoggingHandler = QtHandler.QtHandler()
guiLoggingHandler.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(guiLoggingHandler)


class Googleplus(InputPlugin):
    name = 'googleplus'
    hasWizard = True
    hasRateLimitInfo = False
    hasLocationBasedMode = False

    def __init__(self):
        # Try and read the labels file
        self.http = httplib2.Http()
        labels_config = self.getConfigObj(self.name + '.labels')
        try:
            self.labels = labels_config['labels']
        except Exception, err:
            self.labels = None
            logger.error('Could not load the labels file for the  {0} plugin .'.format(self.name))
            logger.error(err)
        self.config, self.options_string = self.readConfiguration('string_options')
        self.options_boolean = self.readConfiguration('boolean_options')[1]
        self.service = None

    def searchForTargets(self, search_term):
        possibleTargets = []
        logger.debug('Searching for Targets from Google+ Plugin. Search term is : {0}'.format(search_term))
        try:
            if self.service is None:
                self.service = self.getAuthenticatedService()
            peopleResource = self.service.people()
            peopleDocument = peopleResource.search(query=search_term).execute()

            if 'items' in peopleDocument:
                logger.debug('Google+ returned  ' + str(len(peopleDocument['items'])) + ' results')
                for person in peopleDocument['items']:
                    target = {'pluginName': 'GooglePlus Plugin',
                              'targetUserid': person['id'],
                              'targetUsername': person['displayName'],
                              'targetPicture': 'profile_pic_%s' % person['id'],
                              'targetFullname': person['displayName']}
                    # save the pic in the temp folder to show it later
                    filename = 'profile_pic_%s' % person['id']
                    temp_file = os.path.join(GeneralUtilities.getTempDir(), filename)
                    # Retieve and save the profile photo only if it does not exist
                    if not os.path.exists(temp_file):
                        urllib.urlretrieve(person['image']['url'], temp_file)
                    possibleTargets.append(target)
        except Exception, err:
            logger.error(err)
            logger.error('Error searching for targets in Google+ plugin.')
        return possibleTargets

    def getAuthenticatedService(self):
        try:
            credentials = AccessTokenCredentials.new_from_json(self.options_string['hidden_credentials'])
            if credentials.invalid:
                self.http = credentials.refresh(self.http)
            else:
                self.http = credentials.authorize(self.http)
            service = build('plus', 'v1', http=self.http)
            return service
        except Exception, e:
            logger.error(e)
            logger.error('Error getting an authentication context')
            return None

    def runConfigWizard(self):
        try:
            flow = OAuth2WebServerFlow(self.options_string['hidden_application_clientid'],
                                       self.options_string['hidden_application_secret'],
                                       scope='https://www.googleapis.com/auth/plus.login',
                                       redirect_uri='urn:ietf:wg:oauth:2.0:oob')
            authorizationURL = flow.step1_get_authorize_url()
            self.wizard = QWizard()
            self.wizard.setWindowTitle('Google+ plugin configuration wizard')
            page1 = QWizardPage()
            page2 = QWizardPage()
            layout1 = QVBoxLayout()
            layout2 = QVBoxLayout()
            layoutInputPin = QHBoxLayout()

            label1a = QLabel(
                'Click next to connect to Google. Please login with your account and follow the instructions in order \
                to authorize creepy')
            label2a = QLabel(
                'Copy the code that you will receive once you authorize cree.py in the field below and click finish')
            codeLabel = QLabel('Code')
            inputCode = QLineEdit()
            inputCode.setObjectName('inputCode')
            html = QWebView()
            # Url decode the authorization url so that scope and redirect url gets decoded.
            # QWebView will fail to load the url correctly otherwise
            html.load(QUrl(urllib.unquote_plus(authorizationURL)))

            layout1.addWidget(label1a)
            layout2.addWidget(html)
            layout2.addWidget(label2a)
            layoutInputPin.addWidget(codeLabel)
            layoutInputPin.addWidget(inputCode)
            layout2.addLayout(layoutInputPin)

            page1.setLayout(layout1)
            page2.setLayout(layout2)
            page2.registerField('inputCode*', inputCode)
            self.wizard.addPage(page1)
            self.wizard.addPage(page2)
            self.wizard.resize(800, 600)

            if self.wizard.exec_():
                try:
                    credentials = flow.step2_exchange(str(self.wizard.field('inputCode').toString()).strip(), self.http)
                    self.options_string['hidden_credentials'] = credentials.to_json()
                    self.saveConfiguration(self.config)
                except Exception, err:
                    logger.error(err)
                    self.showWarning('Error completing the wizard',
                                     'We were unable to obtain the credentials for your account, please try to run the\
                                      wizard again.')
        except Exception, err:
            logger.error(err)

    def showWarning(self, title, text):
        try:
            QMessageBox.warning(self.wizard, title, text)
        except Exception, err:
            logger(err)

    def isConfigured(self):
        if self.service is None:
            self.service = self.getAuthenticatedService()
        try:
            peopleResource = self.service.people()
            personDocument = peopleResource.get(userId='me').execute()
            return True, ''
        except Exception, err:
            logger.error(err)
            return False, err

    def returnAnalysis(self, target, search_params):
        if self.service is None:
            self.service = self.getAuthenticatedService()
        locations_list = []
        try:
            logger.debug('Attempting to retrieve the activities from Google Plus for user ' + target['targetUserid'])
            activitiesResource = self.service.activities()

            request = activitiesResource.list(userId=target['targetUserid'], collection='public')
            while request:
                activitiesDocument = request.execute()
                logger.debug('{0} activities were retrieved from GooglePlus Plugin'.format(
                    str(len(activitiesDocument['items']))))
                for activity in activitiesDocument['items']:
                    if hasattr(activity, 'location'):
                        loc = {}
                        loc['plugin'] = 'googleplus'
                        loc['context'] = activity['object']['content']
                        loc['infowindow'] = self.constructContextInfoWindow(activity, target['targetUsername'])
                        loc['date'] = dateutil.parser.parse(activity['published'])
                        loc['lat'] = activity['location']['position']['latitude']
                        loc['lon'] = activity['location']['position']['longitude']
                        loc['shortName'] = activity['location']['displayName']
                        loc['accuracy'] = 'high'
                        locations_list.append(loc)
                    elif hasattr(activity, 'geocode'):
                        loc = {}
                        loc['plugin'] = 'googleplus'
                        loc['context'] = activity['object']['content']
                        loc['infowindow'] = self.constructContextInfoWindow(activity, target['targetUsername'])
                        loc['date'] = dateutil.parser.parse(activity['published'])
                        loc['lat'], loc['lon'] = activity['geocode'].split(' ')
                        loc['shortName'] = activity['placeName']
                        loc['accuracy'] = 'high'
                        locations_list.append(loc)
                request = self.service.activities().list_next(request, activitiesDocument)
            logger.debug('{0} locations were retrieved from GooglePlus Plugin'.format(str(len(locations_list))))
        except Exception, e:
            logger.error(e)
            logger.error('Error getting locations from GooglePlus plugin')
        return locations_list, None

    def constructContextInfoWindow(self, activity, username):
        html = unicode(self.options_string['infowindow_html'], 'utf-8')
        return html.replace('@TEXT@', activity['object']['content']).replace('@DATE@', activity['published']).replace(
            '@PLUGIN@', u'googleplus').replace('@USERNAME@', username)

    def getLabelForKey(self, key):
        """
        read the plugin_name.labels 
        file and try to get label text for the key that was asked
        """
        if not self.labels:
            return key
        if key not in self.labels.keys():
            return key
        return self.labels[key]
