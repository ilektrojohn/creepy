#!/usr/bin/python
# -*- coding: utf-8 -*-
from models.InputPlugin import InputPlugin
import flickrapi
import datetime
import logging
import re
import os
from configobj import ConfigObj
from flickrapi.exceptions import FlickrError
#set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(os.path.join(os.getcwdu(),'creepy_main.log'))
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
class Flickr(InputPlugin):
     
    name = "flickr"
    hasWizard = False
    
    
    def __init__(self):
        #Try and read the labels file
        labels_filename = self.name+".labels"
        labels_file = os.path.join(os.getcwdu(),'plugins', self.name, labels_filename)
        labels_config = ConfigObj(infile=labels_file)
        labels_config.create_empty=False
        try:
            logger.debug("Trying to load the labels file for the  "+self.name+" plugin .")
            self.labels = labels_config['labels']
        except Exception,err:
            self.labels = None 
            logger.error("Could not load the labels file for the  "+self.name+" plugin .")  
            logger.exception(err) 
        self.config, self.options_string = self.readConfiguration("string_options")
        self.api = flickrapi.FlickrAPI(self.options_string["hidden_api_key"])
    def searchForTargets(self, search_term):
        
        possibleTargets = []
        try:
            
            # Try to distinguish between mail and username in the search term
            if re.match("[\w\-\.+]+@(\w[\w\-]+\.)+[\w\-]+", search_term): 
                results = self.api.people_findByEmail(find_email=search_term)
            else:
                results = self.api.people_findByUsername(username=search_term)
            
            for userid in results.find('user').items():
                possibleTargets.append(self.getUserInfo(userid[1]))
                
        except Exception, e:
            logger.error(e)
            if e.message == 'Error: 1: User not found':
                logger.info("No results for search query "+search_term+" from Flickr Plugin")
        logger.debug(str(len(possibleTargets))+" possible targets were found matching the search query")
        #Flickr returns 2 entries per user, one with nsid and one with id , they are exactly the same
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
            results = self.api.people_getInfo(user_id=userId)
            if results.attrib['stat'] == 'ok':
                target = {'pluginName':'Flickr Plugin'}
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
            logger.error("Error getting target info from Flickr for target "+userId)
            logger.error(err)
            return None
    
    def isConfigured(self):
        try:
            if not self.options_string:
                self.options_string = self.readConfiguration("string_options")[1]
            api = flickrapi.FlickrAPI(self.options_string["hidden_api_key"])
            api.people_findByUsername(username="testAPIKey");
            return (True, "")
        except Exception, e:
            logger.error("Error establishing connection to Flickr API.")
            logger.error(e)
            return (False, "Error establishing connection to Flickr API. ")
    
    def getPhotosByPage(self, userid, page_nr):
        try:
            results = self.api.people_getPublicPhotos(user_id=userid, extras="geo, date_taken", per_page=500, page=page_nr)
            if results.attrib['stat'] == 'ok':
                return results.find('photos').findall('photo')
        except Exception , err:
            logger.error("Error getting photos per page from Flickr")
            logger.error(err)
            
    def getLocationsFromPhotos(self, photos):  
        locations = []
        if photos:
            for photo in photos:
                try:
                    if photo.attrib['latitude'] != '0':
                        loc = {}
                        loc['plugin'] = "flickr"
                        photo_link = unicode('http://www.flickr.com/photos/%s/%s' % (photo.attrib['owner'], photo.attrib['id']), 'utf-8')
                        title = photo.attrib['title']
                        #If the title is a string, make it unicode
                        if isinstance(title,str):
                            title = title.decode('utf-8')
                        loc['context'] = u'Photo from flickr  \n Title : %s \n ' % (title)
                        loc['date'] = datetime.datetime.strptime(photo.attrib['datetaken'], "%Y-%m-%d %H:%M:%S")
                        loc['lat'] = photo.attrib['latitude']
                        loc['lon'] = photo.attrib['longitude']
                        loc['shortName'] = "Unavailable"
                        loc['infowindow'] = self.constructContextInfoWindow(photo_link, loc['date'])
                        locations.append(loc)
                except Exception,err:
                    logger.error(err)
        return locations      
            
    def returnLocations(self, target, search_params):
        photosList = []
        locationsList = []
        try:
            results = self.api.people_getPublicPhotos(user_id=target['targetUserid'], extras="geo, date_taken", per_page=500)
        
            if results.attrib['stat'] == 'ok':
                res = results.find('photos')
                total_photos = res.attrib['total']
                pages = int(res.attrib['pages'])
                logger.debug("Photo results from Flickr were "+ str(pages) + " pages and " + total_photos+" photos.")
                if pages > 1:
                    for i in range(1, pages + 1, 1):
                        photosList.extend(self.getPhotosByPage(target['targetUserid'], i))
                else:
                    photosList = results.find('photos').findall('photo')
                    
                locationsList = self.getLocationsFromPhotos(photosList)
                return locationsList
                
        except FlickrError, err:
            logger.error("Error getting locations from Flickr")
            logger.error(err)
            
            
    def constructContextInfoWindow(self, link, date):
        html = unicode(self.options_string['infowindow_html'], 'utf-8')
        return html.replace("@LINK@",link).replace("@DATE@",date.strftime("%Y-%m-%d %H:%M:%S %z")).replace("@PLUGIN@", u"flickr")
    
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
        