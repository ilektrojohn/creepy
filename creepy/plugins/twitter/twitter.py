#!/usr/bin/python
# -*- coding: utf-8 -*-
from models.InputPlugin import InputPlugin
import tweepy
import logging
import os
import urllib
from PyQt4.QtGui import QWizard, QWizardPage, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt4.QtCore import QUrl
from PyQt4.QtWebKit import QWebView
from tweepy import Cursor
from configobj import ConfigObj

#set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(os.path.join(os.getcwd(),'creepy_main.log'))
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
class Twitter(InputPlugin):
    
    name = "twitter"
    hasWizard = True
    
    def __init__(self):
        #Try and read the labels file
        labels_filename = self.name+".labels"
        labels_file = os.path.join(os.getcwd(),'plugins', self.name, labels_filename)
        labels_config = ConfigObj(infile=labels_file)
        labels_config.create_empty=False
        try:
            logger.debug("Trying to load the labels file for the  "+self.name+" plugin .")
            self.labels = labels_config['labels']
        except Exception,err:
            self.labels = None 
            logger.error("Could not load the labels file for the  "+self.name+" plugin .")  
            logger.exception(err) 
        
        
        
        self.config,self.options_string = self.readConfiguration("string_options")
        self.options_boolean = self.readConfiguration("boolean_options")[1]
        self.api = self.getAuthenticatedAPI()
    
    def searchForTargets(self, search_term):
        possibleTargets = []
        logger.debug("Searching for Targets from Twitter Plugin. Search term is : "+search_term)
        try:
            api = self.getAuthenticatedAPI()
            search_results = api.search_users(q=search_term)
            if search_results:
                logger.debug("Twitter returned  "+str(len(search_results))+" results")
                for i in search_results:
                    if self.options_boolean['exclude_geo_disabled'] == 'True' and not i.geo_enabled:
                        continue
                    target = {'pluginName':'Twitter Plugin'}
                    target['targetUserid'] = i.id_str
                    target['targetUsername'] = i.screen_name
                    target['targetPicture'] = 'profile_pic_%s' % i.id_str
                    target['targetFullname'] = i.name
                    #save the pic in the temp folder to show it later
                    filename = 'profile_pic_%s' % i.id_str
                    temp_file = os.path.join(os.getcwd(), "temp", filename)
                    #Retieve and save the profile phot only if it does not exist
                    if not os.path.exists(temp_file):
                        urllib.urlretrieve(i.profile_image_url, temp_file)
                    possibleTargets.append(target)
        except Exception, err:
            logger.error(err)
            logger.error("Error searching for targets in Twitter plugin.")
        return possibleTargets
    
    def getAuthenticatedAPI(self):
        try:
            auth = tweepy.auth.OAuthHandler(self.options_string['hidden_application_key'], self.options_string['hidden_application_secret'], secure=True)
            auth.set_access_token(self.options_string['hidden_access_token'], self.options_string['hidden_access_token_secret'])
            return tweepy.API(auth)
        except Exception,e:
            logger.error(e)
            return None
    
    def runConfigWizard(self):
        try:
            oAuthHandler = tweepy.OAuthHandler(self.options_string['hidden_application_key'], self.options_string['hidden_application_secret'], secure=True)
            authorizationURL = oAuthHandler.get_authorization_url(True)
            self.wizard = QWizard()
            page1 = QWizardPage()
            page2 = QWizardPage()
            layout1 = QVBoxLayout()
            layout2 = QVBoxLayout()
            layoutInputPin = QHBoxLayout()
            
            label1a = QLabel("Click next to connect to twitter.com . Please login with your account and follow the instructions in order to authorize creepy")
            label2a = QLabel("Copy the PIN that you will receive once you authorize cree.py in the field below and click finish")
            pinLabel = QLabel("PIN")
            inputPin = QLineEdit()
            inputPin.setObjectName("inputPin")
            
            
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
            page2.registerField("inputPin*", inputPin)
            self.wizard.addPage(page1)
            self.wizard.addPage(page2)
            self.wizard.resize(800,600)
            
            if self.wizard.exec_():
                try:
                    oAuthHandler.get_access_token(str(self.wizard.field("inputPin").toString()).strip())
                    access_token = oAuthHandler.access_token.key
                    access_token_secret = oAuthHandler.access_token.secret
                    self.options_string['hidden_access_token'] = access_token
                    self.options_string['hidden_access_token_secret'] = access_token_secret
                    self.config.write()
                except Exception, err:
                    logger.error(err)
                    self.showWarning("Error completing the wizard", "We were unable to obtain the access token for your account, please try to run the wizard again.")
            
        except Exception,err:
            logger.exception(err)
        
        
    def showWarning(self, title, text):
        try:
            QMessageBox.warning(self.wizard, title, text)  
        except Exception, err:
            print err
        
    """
    Returns the authorization URL for Twitter or None if there was an exception
    """
    def getAuthorizationURL(self):
        try:
            if not self.options_string:
                self.options_string = self.readConfiguration("string_options")[1]
            oAuthHandler = tweepy.OAuthHandler(self.options_string['hidden_application_key'], self.options_string['hidden_application_secret'])
            authorizationURL = oAuthHandler.get_authorization_url(True)
            return authorizationURL
        except Exception, err:
            logger.error(err.reason)
            return None
        
    """
    Returns a tuple. The first element is True or False, depending if the plugin is configured or not. The second
    element contains an optional message for the user
    """
    def isConfigured(self):
        
        try:
            if not self.options_string:
                self.options_string = self.readConfiguration("string_options")[1]
            oAuthHandler = tweepy.OAuthHandler(self.options_string['hidden_application_key'], self.options_string['hidden_application_secret'])
            oAuthHandler.set_access_token(self.options_string['hidden_access_token'], self.options_string['hidden_access_token_secret'])
            api = tweepy.API(oAuthHandler)
            logger.debug(api.me().name)
            return (True, "")
        except Exception, e:
            logger.error("Error authenticating with Twitter API.")
            logger.error(e)
            return (False, "Error authenticating with Twitter. "+e.reason)
        
    
    def returnLocations(self, target, search_params):
        locations_list = []
        cnt = 200
        incl_rts = search_params['boolean']['include_retweets']
        excl_rpls = search_params['boolean']['exclude_replies']
        if not self.api:
            self.api = self.getAuthenticatedAPI()
        try:    
            logger.debug("Attempting to retrieve the tweets for user "+target['targetUserid'])
            tweets = Cursor(self.api.user_timeline, user_id=target['targetUserid'], exclude_replies=excl_rpls, include_rts=incl_rts, count=cnt).items()
            for i in tweets:
                ''' 
                First Handle the coordinates return field
                Twitter API returns GeoJSON, see http://www.geojson.org/geojson-spec.html for the spec    
                We don't handle MultiPoint, LineString, MultiLineString, MultiPolygon and Geometry Collection
                '''
                if i.coordinates and i.place:
                    if i.coordinates['type'] == 'Point':
                        loc = {}
                        loc['plugin'] = "twitter"
                        #this returns unicode!
                        loc['context'] = i.text
                        loc['infowindow'] = self.constructContextInfoWindow(i)                                 
                        loc['date'] = i.created_at
                        loc['lat'] = i.coordinates['coordinates'][1]
                        loc['lon'] = i.coordinates['coordinates'][0]
                        loc['shortName'] = i.place.name
                        locations_list.append(loc)     
                    elif i.coordinates.type == 'PolyGon':
                        loc = {}
                        loc['plugin'] = "twitter"
                        loc['context'] = i.text   
                        loc['infowindow'] = self.constructContextInfoWindow(i)                              
                        loc['date'] = i.created_at
                        c = self.getCenterOfPolygon(i.coordinates['coordinates'])
                        loc['lat'] = c[1]
                        loc['lon'] = c[0]
                        loc['shortName'] = i.place.name
                        locations_list.append(loc)                          
                elif i.place and not i.coordinates:
                    if i.place.bounding_box.type == 'Point':
                        loc = {}
                        loc['plugin'] = "twitter"
                        loc['context'] = i.text    
                        loc['infowindow'] = self.constructContextInfoWindow(i)                             
                        loc['date'] = i.created_at
                        loc['lat'] = i.place.bounding_box.coordinates[1]
                        loc['lon'] = i.place.bounding_box.coordinates[0]
                        loc['shortName'] = i.place.name
                        locations_list.append(loc)        
                    elif i.place.bounding_box.type == 'Polygon':
                        loc = {}
                        loc['plugin'] = "twitter"
                        loc['context'] = i.text        
                        loc['infowindow'] = self.constructContextInfoWindow(i)                         
                        loc['date'] = i.created_at
                        c = self.getCenterOfPolygon(i.place.bounding_box.coordinates[0])
                        loc['lat'] = c[1]
                        loc['lon'] = c[0]
                        loc['shortName'] = i.place.name
                        locations_list.append(loc)  
            logger.debug(str(len(locations_list))+ " were retrieved from Twitter Plugin")                      
        except Exception, e:
            logger.error(e)
            logger.error("Error getting locations from twitter plugin")
        return locations_list    

    def constructContextInfoWindow(self, tweet):
        
        html = unicode(self.options_string['infowindow_html'], 'utf-8')
        #returned value also becomes unicode since tweet.text is unicode, and carries the encoding also
        return html.replace("@TEXT@",tweet.text).replace("@DATE@",tweet.created_at.strftime("%Y-%m-%d %H:%M:%S %z")).replace("@PLUGIN@", u"twitter")
    
    def getCenterOfPolygon(self, coord):
        '''
        We need to get the "center" of the polygon. Accuracy is not a major aspect here since
        we originally got a polygon, so there was not much accuracy to start with. We convert the 
        polygon to a rectangle by selecting 4 points : 
        a) Point with the Lowest latitude
        b) Point with the Highest Latitude
        c) Point with the Lowest Longitude
        d) Point with the Highest Longitude
        
        and then get the center of this rectangle as the point to draw on the map
        '''
        lat_list = []
        lon_list = []
        for j in coord:
            lon_list.append(j[0])
            lat_list.append(j[1])
        lon_list.sort()
        lat_list.sort()
        lat = float(lat_list[0]) + ((float(lat_list[len(lat_list)-1]) - float(lat_list[0])) / 2)
        lon = float(lon_list[0]) + ((float(lon_list[len(lon_list)-1]) - float(lon_list[0])) / 2)
        return (lon, lat)
    
    
    def getLabelForKey(self, key):
        '''
        read the plugin_name.labels 
        file and try to get label text for the key that was asked
        '''
        if not self.labels:
            return key
        if not key in self.labels.keys():
            return key
        return self.labels[key]
        
    