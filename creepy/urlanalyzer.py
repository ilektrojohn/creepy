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


import re
import urllib, simplejson
import pyexiv2
from PIL import Image
from PIL.ExifTags import TAGS
import time
import os.path
from datetime import datetime
from time import  mktime
from urlparse import urlparse
from BeautifulSoup import BeautifulSoup as bs


class URLAnalyzer():
    """
    Class used for shortened URL analyzing
    
    The class helps analyze the shortened URLs found in users tweets. If the URL hold an image the image is downloaded
    and meta data information is extracted. If the shortened URL is from foursquare, the location is retrieved via html scrapping
    """
    def __init__(self, photo_dir, moby_key):
        self.errors = []
        self.photo_dir = photo_dir
        self.moby_key = moby_key
    
    def default_action(self, url, tweet):
        return []
    
    
    def fsq(self, url, tweet):
        """
        Handles foursquare links
        
        returns location coordinates
        """
        try:
            data = {}
            full_url = urllib.urlopen(url.geturl()).url
            if 'checkin' in full_url:
                html = urllib.urlopen(full_url).read()
                coordinates = re.findall('GLatLng\([-+]?([0-9]*\.[0-9]+|[0-9]+)\,[ \t][-+]?([0-9]*\.[0-9]+|[0-9]+)', html)
                if coordinates:
                    data['from'] = 'fsquare_checkin' 
                    data['context'] = 'Information retrieved from foursquare. Tweet was %s ' % (tweet.text)
                    data['time'] = tweet.created_at 
                    data['latitude'] = float(coordinates[0][0])
                    data['longitude'] = float(coordinates[0][1])
            return [data]
        except Exception, err:
            #print 'Error getting location from foursquare', err
            self.errors.append({'from':'foursqare', 'tweetid':tweet.id, 'url': url.geturl() ,'error':err})
            return []
    
   
    def exif_extract(self, temp_file, context):
        def calc(k): return [(float(n)/float(d)) for n,d in [k.split("/")]][0]
        def degtodec(a): return a[0]+a[1]/60+a[2]/3600
        def format_coordinates(string):
            return degtodec([(calc(i)) for i in (string.split(' ')) if ("/" in i)])
                
        
        exif_data = pyexiv2.ImageMetadata(temp_file)
        try:
            exif_data.read()
            if "Exif.GPSInfo.GPSLatitude" in exif_data.exif_keys :
                coordinates = {}
                coordinates['from'] = 'exif'
                coordinates['context'] = 'Location retrieved from image exif metadata .Tweet was %s' % (context)
                coordinates['time'] = datetime.fromtimestamp(mktime(time.strptime(exif_data['Exif.Image.DateTime'].raw_value, "%Y:%m:%d %H:%M:%S")))
                coordinates['latitude'] = format_coordinates(exif_data['Exif.GPSInfo.GPSLatitude'].raw_value)
                lat_ref = exif_data['Exif.GPSInfo.GPSLatitudeRef'].raw_value
                if lat_ref == 'S':
                    coordinates['latitude'] = -coordinates['latitude']
                coordinates['longitude'] = format_coordinates(exif_data['Exif.GPSInfo.GPSLongitude'].raw_value)
                long_ref = exif_data['Exif.GPSInfo.GPSLongitudeRef'].raw_value
                if long_ref == 'W':
                    coordinates['longitude'] = -coordinates['longitude']
                return coordinates
            else:
                return []
        except Exception, err:
            self.errors.append({'from':'exif', 'tweetid':0, 'url':'', 'error':err})
            #print 'Exception  ' , err
     
            
            
    def tp(self, url, tweet):
        '''
        api_location = {}
        try:
            json_reply= simplejson.load(urllib.urlopen("http://api.twitpic.com/2/media/show.json?id="+url.path[1:]))
            if 'location' in json_reply :
                api_location['from'] = 'twitpic_api'
                api_location['time'] = json_reply['timestamp']
                api_location['coordinates'] = json_reply['location']
        except simplejson.JSONDecodeError:
            #print "error produced by http://api.twitpic.com/2/media/show.json?id="+url.path[1:]
        '''             
       
        
        try:
            #Handle some bad HTML in twitpic
            html = urllib.urlopen(url.geturl()).read()
            html = html.replace('</sc"+"ript>','')
            soup = bs(html)
            #Grabs the photo from Amazon cloud 
            temp_file = os.path.join(self.photo_dir,url.path[1:])
            photo_url = soup.find(attrs={"class": "photo", "id": "photo-display"})['src']
            urllib.urlretrieve(photo_url , temp_file)
            return [self.exif_extract(temp_file, tweet.text)] 
        except Exception, err: 
            #print 'Error trying to download %s ' % (url.geturl()),err
            self.errors.append({'from':'twitpic', 'tweetid':tweet.id, 'url': url.geturl(), 'error':err})
            return []
             
        
                
    def yfrog(self, url, tweet):
        
        try:
            ip = bs(urllib.urlopen("http://yfrog.com/api/xmlInfo?path="+url.path[1:])).find('ip')
            if ip:
                pass
                #print ip.string
        except Exception, err:
            pass
            #print 'Exception ', err
        
        try:
            soup = bs(urllib.urlopen(url.geturl()))
            temp_file = os.path.join(self.photo_dir,url.path[1:])
            photo_url = soup.find(attrs={"rel": "image_src"})['href'] 
            urllib.urlretrieve(photo_url, temp_file)
            return [self.exif_extract(temp_file, tweet.text)]
        except Exception, err:
            #print 'Error trying to download %s ' % (photo_url),err
            self.errors.append({'from':'yfrog', 'tweetid':tweet.id, 'url': url.geturl() ,'error':err})
            return []
        
    def imgly(self, url, tweet):
        try:
            soup = bs(urllib.urlopen(url.geturl()))
            temp_file = os.path.join(self.photo_dir,url.path[1:])
            photo_url = "http://img.ly"+soup.find(attrs={"id": "the-image"})['src']
            urllib.urlretrieve(photo_url, temp_file)
            return [self.exif_extract(temp_file, tweet.text)]
        except Exception, err:
            #print 'Error trying to download %s ' % (photo_url),err
            self.errors.append({'from':'imgly', 'tweetid':tweet.id, 'url': url.geturl() ,'error':err})
            return []
            
    def plixi(self, url, tweet):
        api_location ={}
        try:
            json_reply= simplejson.load(urllib.urlopen("http://api.plixi.com/api/tpapi.svc/json/photos/"+url.path[3:]))
            api_location['from'] = 'plixi_api'
            api_location['context'] = 'Location retrieved from plixi API. Original tweet was %s' % (tweet.text)
            api_location['latitude'] = json_reply['Location']['Latitude'] 
            api_location['longitude'] = json_reply['Location']['Longitude']
            api_location['time'] = datetime.fromtimestamp(json_reply['UploadDate'])
            ''' html = urllib.urlopen("http://plixi.com/photos/original/"+url.path[3:]).read()
            temp_file = os.path.join(self.photo_dir,url.path[3:])
            #print re.findall("http://[\S]+cloudfiles[\S]+", html)
            urllib.urlretrieve(re.findall("http://[\S]+cloudfiles[\S]+", html), temp_file)
            '''
        except Exception, err:
            self.errors.append({'from':'plixi', 'tweetid':tweet.id, 'url': url.geturl() ,'error':err})
        return [api_location]
    
    def twitrpix(self, url, tweet):
        try:
            temp_file = os.path.join(self.photo_dir, url.path[1:])
            photo_url = "http://img.twitrpix.com"+url.path
            urllib.urlretrieve(photo_url, temp_file)
            return [self.exif_extract(temp_file, tweet.text)]
        except Exception, err:
            #print 'Error trying to download %s ' % (photo_url),err
            self.errors.append({'from':'twitrpix', 'tweetid':tweet.id, 'url': url.geturl() ,'error':err})
            return []
         
    def folext(self, url, tweet):
        try:
            temp_file = os.path.join(self.photo_dir,url.path[1:])
            photo_url = "http://img.folext.com"+url.path+".jpg"    
            urllib.urlretrieve(photo_url, temp_file)
            return [self.exif_extract(temp_file, tweet.text)]
        except Exception, err:
            #print 'Error trying to download %s ' % (photo_url),err
            self.errors.append({'from':'folext', 'tweetid':tweet.id, 'url': url.geturl() ,'error':err})
            return []
        
    def shozu(self, url, tweet):
        try:
            soup = bs(urllib.urlopen(url.geturl()))
            temp_file = os.path.join(self.photo_dir, url.path[3:])
            photo_url = soup.find(attrs={"class": "cls"})['src']
            urllib.urlretrieve(photo_url, temp_file)
            return [self.exif_extract(temp_file, tweet.text)]
        except Exception, err:
            #print 'Error trying to download %s ' % (photo_url),err
            self.errors.append({'from':'shozu', 'tweetid':tweet.id, 'url': url.geturl() ,'error':err})
            return []
        
    def pikchur(self, url, tweet):
        '''
        Original photo not available so not much info to come from edited/resized pics. Discard? 
        '''
        try:
            temp_file = os.path.join(self.photo_dir,url.path[1:])
            photo_url = "http://img.pikchur.com/pic_"+url.path[1:]+"_l.jpg"
            urllib.urlretrieve(photo_url, temp_file)
            return [self.exif_extract(temp_file, tweet.text)]
        except Exception, err:
            #print 'Error trying to download %s ' % (photo_url),err
            self.errors.append({'from':'pickhur', 'tweetid':tweet.id, 'url': url.geturl() ,'error':err})
            return []
    
    def moby(self, url, tweet):
        api_loc= {}
        try:
            json_reply = simplejson.load(urllib.urlopen("http://api.mobypicture.com/?t="+url.path[1:]+"&action=getMediaInfo&k="+self.moby_key+"&format=json"))
            if json_reply['post']['location_latlong']:
                api_loc['from'] = "moby_api"
                api_loc['context'] = 'Location retrieved from moby.to API. Original tweet was %s' % (tweet.text)
                api_loc['latitude'] = json_reply['post']['location_latlong'][0]
                api_loc['longitude'] = json_reply['post']['location_latlong'][1]
                api_loc['time'] = datetime.fromtimestamp(json_reply['created_on_epoch'])
        
            temp_file = os.path.join(self.photo_dir, url.path[1:])
            photo_url = str(json_reply['post']['media']['url_full']).replace('large', 'full')
            urllib.urlretrieve(photo_url, temp_file)
            return [api_loc, self.exif_extract(temp_file, tweet.text)]
        except Exception, err:
            #print 'Error trying to download %s ' % (photo_url),err
            self.errors.append({'from':'moby', 'tweetid':tweet.id, 'url': url.geturl() ,'error':err})
        return [api_loc]
    
    def twitsnaps(self, url, tweet):
        try:
            temp_file = os.path.join(self.photo_dir, url.path[1:])
            photo_url = "http://twitsnaps.com/snap"+url.path
            urllib.urlretrieve(photo_url, temp_file)
            return [self.exif_extract(temp_file, tweet.text)]
        except Exception, err:
            #print 'Error trying to download %s ' % (photo_url),err
            self.errors.append({'from':'twitsnaps', 'tweetid':tweet.id, 'url': url.geturl() ,'error':err})
            return []
        
    def twitgoo(self, url, tweet):
        try:
            img_url = bs(urllib.urlopen("http://twitgoo.com/api/message/info"+url.path)).find('imageurl').string
            temp_file = os.path.join(self.photo_dir,url.path[1:])
            urllib.urlretrieve(img_url, temp_file)
            return [self.exif_extract(temp_file, tweet.text)]
        except Exception, err:
            #print 'Error trying to download %s ' % (img_url),err
            self.errors.append({'from':'twitgoo', 'tweetid':tweet.id, 'url': url.geturl() ,'error':err})
            return []
        
    def get_photo_location(self, tweet):            
        service = {'4sq.com': self.fsq,
                   'twitpic.com' : self.tp,
                   'yfrog.com': self.yfrog,
                   'img.ly'  : self.imgly,
                   'plixi.com': self.plixi,
                   'twitrpix.com': self.twitrpix,
                   'folext.com': self.folext,
                   'shozu.com': self.shozu,
                   'pikchur.com': self.pikchur,
                   'pk.gd': self.pikchur,
                   'moby.to': self.moby,
                   'twitsnaps.com': self.twitsnaps,
                   'twitgoo.com':self.twitgoo}
        
        final_locations_list=[]
        for i in re.findall("(https?://[\S]+)", tweet.text):  
            url = urlparse(i)
            try:
                for loc in service.get(url.netloc, self.default_action)(url, tweet):
                    if loc:
                        final_locations_list.append(loc)
            except Exception, err:
                self.errors.append({'from':'creepy', 'tweetid':0, 'url':'', 'error':err})
        return (final_locations_list, self.errors)
                           
        
                
        
            
