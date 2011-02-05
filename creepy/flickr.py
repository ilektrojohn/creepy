'''
Copyright 2010 Yiannis Kakavas

This file is part of creepy.

    creepy is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    creepy is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with creepy  If not, see <http://www.gnu.org/licenses/>.
    
'''

import urllib
import flickrapi
from flickrapi.exceptions import FlickrError
import re
from BeautifulSoup import BeautifulSoup as bs


class Flickr():
    """
    Wrapper class for the Flickr API. 
    
    provides functionality for user search and information retrieval
    """

    def __init__(self, conf_file):
    
        self.api = flickrapi.FlickrAPI(conf_file['flickr']['api_key'])
        self.photo_dir = conf_file['directories']['profilepics_dir']

    def search_real_name(self, input):
        """
        Search user by real name
        
        Provides search function by real name. This is not provided by flickr API so
        it needs to be done the old(html-scrapping) way.
        Returns a list of user dictionaries
        """
        html = urllib.urlopen("http://www.flickr.com/search/people/?see=none&q=" + input + "&m=names").read()
        '''
        Removing some javascript that choked BeautifulSoup's parser
        '''
        html = re.sub("(?is)(<script[^>]*>)(.*?)(</script>)", "", html)
        soup = bs(html)
        id = []
        username = []
        name = []
        for r in soup.findAll('h2'):
            id_temp = r.a['href'].replace("/photos/", "")[:-1]
            if re.match(r'[\d]+@[A-Z][\d]+', id_temp):
                id.append(id_temp)
            else:
                id.append(self.getid_from_name(r.a.string))
            username.append(r.a.string)
            try:
                name.append(r.next.next.next.next.b.string)
            except Exception:
                name.append("")
        pics = [p.img['src'] for p in soup.findAll(attrs={"class":"Icon"})]
        user_list = zip(id, username, name, pics)
        users = []
        for user in user_list:
            try:
                temp_file = '%sprofile_pic_%s' % (self.photo_dir, user[0])
                urllib.urlretrieve(user[3], temp_file)
            except Exception, err:
                print 'Error retrieving %s profile picture' % (user[1]), err
            users.append({'id':user[0], 'username': user[1], 'realname':user[2], 'location':'' })
        
        return users



    def search_user(self, input):
        """
        Wrapper to the search function provided by flickr API
        
        Returns a list of user dictionaries
        """
        
        if re.match("[\w\-\.+]+@(\w[\w\-]+\.)+[\w\-]+", input):
            try: 
                results = self.api.people_findByEmail(find_email=input)
            except FlickrError:
                return
        else:
            try:
                results = self.api.people_findByUsername(username=input)
            except FlickrError, err:
                print 'Error from flickr api ', err
                return
        if results.attrib['stat'] == "ok":
            user_list = []
            print results.find('user')
            for i in results.find('user').items():
                user_list.append(self.get_user_info(i[1]))
            return user_list
            
    def getid_from_name(self, username):            
        """
        Gets user's nsid from flickr
        
        Returns user's nsid
        """
        try:
            result = self.api.people_findByUsername(username=username)
            return result.find('user').attrib['nsid']
        except FlickrError, err:
            print 'Error from flickr api ', err
            return
        
    def get_user_info(self, id):
        """
        Retrieves a user's username, real name and location as provided by flickr API
        
        Returns a user dictionary
        """
        
        results = self.api.people_getInfo(user_id=id)
        if results.attrib['stat'] == 'ok':
            user = {'id':id, 'username':'', 'realname':'', 'location':''}
            res = results.find('person')
            user['username'] = res.find('username').text
            if res.find('realname'):
                user['realname'] = res.find('realname').text
            if res.find('location'):
                user['location'] = res.find('location').text
            return user

    
    def get_user_photos(self, id, page_nr):
        """
        Retrieves a users public photos. 
        
        Authentication and retrieval of protected photos is not yet implemented
        Returns a list with all the photos 
        """
        results = self.api.people_getPublicPhotos(user_id=id, extras="geo, date_taken", per_page=500, page=page_nr)
        if results.attrib['stat'] == 'ok':
            return results.find('photos').findall('photo')
        
    
 
    def get_locations(self, photos):
        """
        Determines location information from a list of photos
        
        Extracts the geo data provided by flickr API and returns a
        dictionary of locations
        """
        locations = []
        if photos:
            for photo in photos:
                if photo.attrib['latitude'] != '0':
                    loc = {}
                    loc['context'] = 'Photo from flickr  \n \
                            Title : %s \n \
                            See photo at http://www.flickr.com/photos/%s/%s' % (photo.attrib['title'], photo.attrib['owner'], photo.attrib['id'])
                    loc['time'] = photo.attrib['datetaken']
                    loc['latitude'] = photo.attrib['latitude']
                    loc['longitude'] = photo.attrib['longitude']
                    loc['accuracy'] = photo.attrib['accuracy']
                    locations.append(loc)
        return locations

    def return_locations(self, id):
        """
        Wrapper function for the location retrieval. 
        
        Returns all the locations detected from the user's photos
        """
        locations_list = []
        results = self.api.people_getPublicPhotos(user_id=id, extras="geo, date_taken", per_page=500)
        if results.attrib['stat'] == 'ok':
            res = results.find('photos')
            total_photos = res.attrib['total']
            pages = int(res.attrib['pages'])
            print "pages :" + str(pages) + " , total :" + total_photos
            if pages > 1:
                for i in range(1, pages + 1, 1):
                    locations_list.extend(self.get_locations(self.get_user_photos(id, i)))
            else:
                locations_list.extend(self.get_locations(results.find('photos').findall('photo')))
        return locations_list
