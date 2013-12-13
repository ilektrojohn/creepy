from InputPlugin import InputPlugin
import flickrapi
import datetime
import logging
import re
from flickrapi.exceptions import FlickrError
class Flickr(InputPlugin):
    
    name = "flickr"
    hasWizard = False
    
    
    def __init__(self):
        self.config, self.options_string = self.readConfiguration("string_options")
        self.api = flickrapi.FlickrAPI(self.options_string["api_key"])
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
                
        except FlickrError, e:
            logging.log(logging.ERROR,e)
            if e.message == 'Error: 1: User not found':
                logging.info("No results for search query "+search_term+" from Flickr Plugin")
            return None
        
        #Flickr returns 2 entries per user, one with nsid and one with id , they are exactly the same
        return [dict(t) for t in set([tuple(d.items()) for d in possibleTargets])]
    
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
            logging.log(logging.ERROR, "Error getting target info from Flickr for target "+userId)
            logging.log(logging.ERROR, err)
            return None
    
    def isConfigured(self):
        try:
            if not self.options_string:
                self.options_string = self.readConfiguration("string_options")[1]
            api = flickrapi.FlickrAPI(self.options_string["api_key"])
            api.people_findByUsername(username="testAPIKey");
            return (True, "")
        except Exception, e:
            logging.log(logging.ERROR, "Error establishing connection to Flickr API.")
            logging.log(logging.ERROR,e)
            return (False, "Error establishing connection to Flickr API. ")
    
    def getPhotosByPage(self, id, page_nr):
        try:
            results = self.api.people_getPublicPhotos(user_id=id, extras="geo, date_taken", per_page=500, page=page_nr)
            if results.attrib['stat'] == 'ok':
                return results.find('photos').findall('photo')
        except Exception , err:
            logging.error("Error getting photos per page from Flickr")
            logging.error(err)
            
    def getLocationsFromPhotos(self, photos):  
        locations = []
        if photos:
            for photo in photos:
                if photo.attrib['latitude'] != '0':
                    loc = {}
                    loc['plugin'] = "flickr"
                    photo_link = 'http://www.flickr.com/photos/%s/%s' % (photo.attrib['owner'], photo.attrib['id'])
                    loc['context'] = (photo_link, 'Photo from flickr  \n Title : %s \n ' % (photo.attrib['title']))      
                    loc['date'] = datetime.datetime.strptime(photo.attrib['datetaken'], "%Y-%m-%d %H:%M:%S")
                    loc['lat'] = photo.attrib['latitude']
                    loc['lon'] = photo.attrib['longitude']
                    loc['shortName'] = "Unavailable"
                    loc['infowindow'] = self.constructContextInfoWindow(photo_link, loc['date'])
                    locations.append(loc)
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
                logging.debug("Photo results from Flickr were "+ str(pages) + " pages and " + total_photos+" photos.")
                if pages > 1:
                    for i in range(1, pages + 1, 1):
                        photosList.extend(self.getPhotosByPage(target['targetUserid'], i))
                else:
                    photosList = results.find('photos').findall('photo')
                    
                locationsList = self.getLocationsFromPhotos(photosList)
                return locationsList
                
        except FlickrError, err:
            logging.error("Error getting locations from Flickr")
            logging.error(err)
            
            
    def constructContextInfoWindow(self, link, date):
        html = self.options_string['infowindow_html']
        return html.replace("@LINK@",link).replace("@DATE@",date.strftime("%a %b %d,%H:%M:%S %z")).replace("@PLUGIN@", "flickr")
        