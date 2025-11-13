#!/usr/bin/python
# -*- coding: utf-8 -*-
import pytz
from models.InputPlugin import InputPlugin
import flickrapi
import datetime
import logging
import re
import os
from PyQt4.QtGui import QWizard, QWizardPage, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout
from PyQt4.QtCore import QUrl
from PyQt4.QtWebKit import QWebView
from flickrapi.exceptions import FlickrError
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


class Flickr(InputPlugin):
    name = 'flickr'
    hasWizard = True
    hasRateLimitInfo = False
    hasLocationBasedMode = True

    def __init__(self):
        # Try and read the labels file
        labels_config = self.getConfigObj(self.name + '.labels')
        try:
            self.labels = labels_config['labels']
        except Exception, err:
            self.labels = None
            logger.error('Could not load the labels file for the  ' + self.name + ' plugin .')
            logger.error(err)
        self.config, self.options_string = self.readConfiguration('string_options')
        self.api = None

    def getAuthenticatedAPI(self):
        try:
            token = flickrapi.auth.FlickrAccessToken(unicode(self.options_string['hidden_access_token']),
                                                     unicode(self.options_string['hidden_access_token_secret']),
                                                     u'read')
            flickr = flickrapi.FlickrAPI(self.options_string['hidden_api_key'],
                                         self.options_string['hidden_api_secret'], cache=False, store_token=False,
                                         token=token)
            if flickr.token_valid(perms=u'read'):
                return flickr
            else:
                logger('Error getting an authenticated instance of the flickr API.')
                return None
        except Exception, err:
            logger.error(err)
            return None

    def searchForTargets(self, search_term):
        if self.api is None:
            self.api = self.getAuthenticatedAPI()
        possibleTargets = []
        try:
            # Try to distinguish between mail and username in the search term
            if re.match("[\w\-\.+]+@(\w[\w\-]+\.)+[\w\-]+", search_term):
                results = self.api.people_findByEmail(find_email=unicode(search_term))
            else:
                results = self.api.people_findByUsername(username=unicode(search_term))

            for userid in results.find('user').items():
                possibleTargets.append(self.getUserInfo(userid[1]))

        except Exception, e:
            logger.error(e)
            if e.message == 'Error: 1: User not found':
                logger.info('No results for search query ' + search_term + ' from Flickr Plugin')
        logger.debug(str(len(possibleTargets)) + ' possible targets were found matching the search query')
        # Flickr returns 2 entries per user, one with nsid and one with id , they are exactly the same
        if possibleTargets:
            return [dict(t) for t in set([tuple(d.items()) for d in possibleTargets])]
        else:
            return []

    def getUserInfo(self, userId):
        """
        Retrieves a target's username, real name and location as provided by flickr API
        
        Returns a target dictionary
        """
        try:
            if self.api is None:
                self.api = self.getAuthenticatedAPI()
            results = self.api.people_getInfo(user_id=userId)
            if results.attrib['stat'] == 'ok':
                target = {'pluginName': 'Flickr Plugin'}
                res = results.find('person')
                target['targetUserid'] = userId
                target['targetUsername'] = res.find('username').text
                target['targetPicture'] = "d"
                if res.find('realname'):
                    target['targetFullname'] = res.find('realname').text
                else:
                    target['targetFullname'] = 'Unavailable'
                return target
            else:
                return None
        except Exception, err:
            logger.error('Error getting target info from Flickr for target ' + userId)
            logger.error(err)
            return None

    def isConfigured(self):
        try:
            if not self.options_string:
                self.options_string = self.readConfiguration('string_options')[1]
            if self.api is None:
                self.api = self.getAuthenticatedAPI()
            self.api.people_findByUsername(username='testAPIKey')
            return True, ''
        except Exception, e:
            logger.error('Error establishing connection to Flickr API.')
            logger.error(e)
            return False, 'Error establishing connection to Flickr API.'

    def getPhotosByPage(self, userid, page_nr):
        if self.api is None:
            self.api = self.getAuthenticatedAPI()
        try:
            results = self.api.people_getPublicPhotos(user_id=unicode(userid),
                                                      extras='geo, date_taken, url_m, owner_name', per_page=500,
                                                      page=page_nr)
            if results.attrib['stat'] == 'ok':
                return results.find('photos').findall('photo')
            else:
                return []
        except Exception, err:
            logger.error('Error getting photos per page from Flickr')
            logger.error(err)
            return []

    def getLocationsFromPhotos(self, photos, target):
        locations = []
        if photos:
            for photo in photos:
                try:
                    if photo.attrib['latitude'] != '0':
                        loc = {}
                        loc['plugin'] = 'flickr'
                        loc['username'] = photo.attrib['ownername']
                        photo_link = unicode(
                            'http://www.flickr.com/photos/%s/%s' % (photo.attrib['owner'], photo.attrib['id']), 'utf-8')
                        title = photo.attrib['title']
                        # If the title is a string, make it unicode
                        if isinstance(title, str):
                            title = title.decode('utf-8')
                        loc['context'] = u'Photo from flickr  \n Title : {0} \n '.format(title)
                        loc['date'] = pytz.utc.localize(
                            datetime.datetime.strptime(photo.attrib['datetaken'], '%Y-%m-%d %H:%M:%S'))
                        loc['lat'] = photo.attrib['latitude']
                        loc['lon'] = photo.attrib['longitude']
                        loc['accuracy'] = 'high'
                        loc['shortName'] = 'Unavailable'
                        loc['media_url'] = photo.attrib['url_m']
                        loc['infowindow'] = self.constructContextInfoWindow(photo_link, loc['date'], loc['media_url'],
                                                                            loc['username'])
                        locations.append(loc)
                except Exception, err:
                    logger.error(err)
        return locations

    def returnAnalysis(self, target, search_params):
        photosList = []
        locationsList = []
        if self.api is None:
            self.api = self.getAuthenticatedAPI()
        try:
            results = self.api.people_getPublicPhotos(user_id=unicode(target['targetUserid']),
                                                      extras='geo, date_taken, url_m, owner_name',
                                                      per_page=500)

            if results.attrib['stat'] == 'ok':
                res = results.find('photos')
                total_photos = res.attrib['total']
                pages = int(res.attrib['pages'])
                logger.debug('Photo results from Flickr were ' + str(pages) + ' pages and ' + total_photos + ' photos.')
                if pages > 1:
                    for i in range(1, pages + 1, 1):
                        photosList.extend(self.getPhotosByPage(unicode(str(target['targetUserid'])), i))
                else:
                    photosList = results.find('photos').findall('photo')

                locationsList = self.getLocationsFromPhotos(photosList, target)
        except FlickrError, err:
            logger.error('Error getting locations from Flickr')
            logger.error(err)
        return locationsList, None

    def searchForResultsNearPlace(self, geocode):
        locationsList = []
        if self.api is None:
            self.api = self.getAuthenticatedAPI()
        try:
            if geocode.split(',')[2].endswith('km'):
                radius = geocode.split(',')[2].replace('km', '')
            else:
                radius = str(int(geocode.split(',')[2].replace('m', '')) / 1000)
            logger.debug('Searching Flickr for photos around {0},{1} with radius {2} km'.format(geocode.split(',')[0],
                                                                                                geocode.split(',')[1],
                                                                                                radius))
            # Search for only the last 12 days
            mintakendate = datetime.date.today() - datetime.timedelta(days=12)
            for photo in self.api.walk(has_geo='1', per_page=500, lat=geocode.split(',')[0], lon=geocode.split(',')[1],
                                       radius=radius, extras='geo, date_taken, url_m, owner_name',
                                       min_taken_date=mintakendate.strftime('%Y-%m-%d %H:%M:%S')):
                loc = {}
                loc['plugin'] = 'flickr'
                loc['username'] = photo.attrib['ownername']
                photo_link = unicode(
                    'http://www.flickr.com/photos/%s/%s' % (photo.attrib['owner'], photo.attrib['id']), 'utf-8')
                title = photo.attrib['title']
                # If the title is a string, make it unicode
                if isinstance(title, str):
                    title = title.decode('utf-8')
                loc['context'] = u'Photo from flickr  \n Title : {0} \n '.format(title)
                loc['date'] = pytz.utc.localize(
                    datetime.datetime.strptime(photo.attrib['datetaken'], '%Y-%m-%d %H:%M:%S'))
                loc['lat'] = photo.attrib['latitude']
                loc['lon'] = photo.attrib['longitude']
                loc['accuracy'] = 'high'
                loc['shortName'] = 'Unavailable'
                loc['media_url'] = photo.attrib['url_m']
                loc['infowindow'] = self.constructContextInfoWindow(photo_link, loc['date'], loc['media_url'],
                                                                    loc['username'])
                locationsList.append(loc)
            logger.debug('Retrieved {0} photos from Flickr'.format(len(locationsList)))
        except FlickrError, err:
            logger.error('Error getting locations from Flickr')
            logger.error(err)
        return locationsList

    def runConfigWizard(self):
        try:
            flickr = flickrapi.FlickrAPI(self.options_string['hidden_api_key'],
                                         self.options_string['hidden_api_secret'], cache=False, store_token=False)
            flickr.get_request_token(oauth_callback='oob')
            authorizationURL = flickr.auth_url(perms=u'read')

            self.wizard = QWizard()
            self.wizard.setWindowTitle('Flickr plugin configuration wizard')
            page1 = QWizardPage()
            page2 = QWizardPage()
            layout1 = QVBoxLayout()
            layout2 = QVBoxLayout()
            layoutInputPin = QHBoxLayout()

            label1a = QLabel(
                'Click next to connect to flickr.com . Please login with your account and follow the instructions in \
                order to authorize creepy')
            label2a = QLabel(
                'Copy the PIN that you will receive once you authorize cree.py in the field below and click finish')
            pinLabel = QLabel('PIN')
            inputPin = QLineEdit()
            inputPin.setObjectName('inputPin')

            html = QWebView()
            html.load(QUrl(authorizationURL))

            layout1.addWidget(label1a)
            layout2.addWidget(html)
            layout2.addWidget(label2a)
            layoutInputPin.addWidget(pinLabel)
            layoutInputPin.addWidget(inputPin)
            layout2.addLayout(layoutInputPin)

            page1.setLayout(layout1)
            page2.setLayout(layout2)
            page2.registerField('inputPin*', inputPin)
            self.wizard.addPage(page1)
            self.wizard.addPage(page2)
            self.wizard.resize(800, 600)

            if self.wizard.exec_():
                try:
                    verifier = unicode(self.wizard.field('inputPin').toString())
                    flickr.get_access_token(verifier)
                    self.options_string['hidden_access_token'] = flickr.token_cache.token.token
                    self.options_string['hidden_access_token_secret'] = flickr.token_cache.token.token_secret
                    self.saveConfiguration(self.config)
                except Exception, err:
                    logger.error(err)
                    self.showWarning('Error completing the wizard',
                                     'We were unable to obtain the access token for your account, please try \
                                     to run the wizard again.')

        except Exception, err:
            logger.error(err)

    def constructContextInfoWindow(self, link, date, media_url, username):
        html = unicode(self.options_string['infowindow_html'], 'utf-8')
        return html.replace('@LINK@', link).replace('@DATE@', date.strftime('%Y-%m-%d %H:%M:%S %z')).\
            replace('@PLUGIN@', u'flickr').replace('@MEDIA_URL@', media_url).replace('@USERNAME@', username)

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
