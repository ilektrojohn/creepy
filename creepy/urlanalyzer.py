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
import urllib2
import unicodedata
import dateutil.relativedelta as rl


import time
import os.path
from datetime import datetime
from time import  mktime
from urlparse import urlparse
from BeautifulSoup import BeautifulSoup as bs

try:
    import pyexiv2
except ImportError:
    PYEXIV_AVAILABLE = False
else:
    PYEXIV_AVAILABLE = True

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
                coordinates = re.findall('GLatLng\(([-+]?[0-9]*\.[0-9]+|[0-9]+)\,[ \t]([-+]?[0-9]*\.[0-9]+|[0-9]+)', html)
                if coordinates:
                    data['from'] = 'fsquare_checkin' 
                    data['context'] = ('https://twitter.com/%s/status/%s' % (tweet.user.screen_name, tweet.id) ,'Information retrieved from foursquare.\n  Tweet was %s  \n' % (tweet.text))
                    data['time'] = tweet.created_at 
                    data['latitude'] = float(coordinates[0][0])
                    data['longitude'] = float(coordinates[0][1])
                    data['realname'] = tweet.user.name
            return [data]
        except Exception:
            err = 'Error getting location from foursquare'
            self.errors.append({'from':'foursqare', 'tweetid':tweet.id, 'url': url.geturl() ,'error':err})
            return []
    
    def gowalla(self, url, tweet):
        """
		Handles  gowalla links
		
		returns location coordinates
		"""
        try:
            data = {}
            full_url = urllib.urlopen(url.geturl()).url
            if '/checkins/' in full_url:
                html = urllib.urlopen(full_url).read()
                coordinates = re.findall('center=([-+]?[0-9]*\.[0-9]+|[0-9]+),([-+]?[0-9]*\.[0-9]+|[0-9]+)&', html)
                data['from'] = 'Gowalla_checkin'
                data['context'] = ('https://twitter.com/%s/status/%s' % (tweet.user.screen_name, tweet.id) ,'Information retrieved from Gowalla. \n Tweet was %s  \n' % (tweet.text))				
                data['time'] = tweet.created_at
                data['longitude'] = float(coordinates[0][1])
                data['latitude'] = float(coordinates[0][0])
                data['realname'] = tweet.user.name
            return [data] 
        except Exception:
            err = 'Error getting location from Gowalla'
            self.errors.append({'from':'gowalla', 'tweetid':tweet.id, 'url':url.geturl(), 'error':err})
            return []


    def exif_extract(self, temp_file, tweet):
        """
        Attempt to extract exif information from the provided tweet.
        If pyexiv2 dependency is not installed, this will not work and will
        merely return an empty list
        """

        if not PYEXIV_AVAILABLE:
            return []

        def calc(k): return [(float(n)/float(d)) for n,d in [k.split("/")]][0]
        def degtodec(a): return a[0]+a[1]/60+a[2]/3600
        def format_coordinates(string):
            return degtodec([(calc(i)) for i in (string.split(' ')) if ("/" in i)])
        def format_coordinates_alter(tuple):
            return degtodec(((float(tuple[0].numerator)/float(tuple[0].denominator)), (float(tuple[1].numerator)/float(tuple[1].denominator)), (float(tuple[2].numerator)/float(tuple[2].denominator))))
            
        
        try:
            #Check if pyexiv2 v0.3 is installed
            if 'ImageMetadata' in dir(pyexiv2):
                exif_data = pyexiv2.ImageMetadata(temp_file)
                exif_data.read()
                keys = exif_data.exif_keys
                if "Exif.GPSInfo.GPSLatitude" in keys :
                    coordinates = {}
                    coordinates['from'] = 'exif'
                    coordinates['context'] = ('https://twitter.com/%s/status/%s' % (tweet.user.screen_name, tweet.id) , 'Location retrieved from image exif metadata .\n Tweet was %s \n ' % (tweet.text))
                    coordinates['time'] = datetime.fromtimestamp(mktime(time.strptime(exif_data['Exif.Image.DateTime'].raw_value, "%Y:%m:%d %H:%M:%S")))
                    coordinates['latitude'] = format_coordinates(exif_data['Exif.GPSInfo.GPSLatitude'].raw_value)
                    coordinates['realname'] = tweet.user.name
                    lat_ref = exif_data['Exif.GPSInfo.GPSLatitudeRef'].raw_value
                    if lat_ref == 'S':
                        coordinates['latitude'] = -coordinates['latitude']
                    coordinates['longitude'] = format_coordinates(exif_data['Exif.GPSInfo.GPSLongitude'].raw_value)
                    long_ref = exif_data['Exif.GPSInfo.GPSLongitudeRef'].raw_value
                    if long_ref == 'W':
                        coordinates['longitude'] = -coordinates['longitude']
                    
                    if coordinates['longitude'] == 0 and coordinates['latitude'] == 0:
                        return []
                    else:
                        return coordinates
                else:
                    return []
            else:
                exif_data = pyexiv2.Image(temp_file)
                exif_data.readMetadata()
                keys = exif_data.exifKeys
                if 'Exif.GPSInfo.GPSLatitude' in exif_data.exifKeys():
                    coordinates = {}
                    coordinates['from'] = 'exif'
                    coordinates['time'] = exif_data['Exif.Image.DateTime']
                    coordinates['context'] = ('https://twitter.com/%s/status/%s' % (tweet.user.screen_name, tweet.id) , 'Location retrieved from image exif metadata .\n Tweet was %s \n ' % (tweet.text))
                    coordinates['latitude'] = format_coordinates_alter(exif_data['Exif.GPSInfo.GPSLatitude'])
                    coordinates['realname'] = tweet.user.name
                    lat_ref = exif_data['Exif.GPSInfo.GPSLatitudeRef']
                    if lat_ref == 'S':
                        coordinates['latitude'] = -coordinates['latitude']
                    coordinates['longitude'] = format_coordinates_alter(exif_data['Exif.GPSInfo.GPSLongitude'])
                    long_ref = exif_data['Exif.GPSInfo.GPSLongitudeRef']
                    if long_ref == 'W':
                        coordinates['longitude'] = -coordinates['longitude']
                        
                    if coordinates['longitude'] == 0 and coordinates['latitude'] == 0:
                        return []
                    else:
                        return coordinates
                else:
                    return []   
        except Exception:
            err = 'Error extracting gps coordinates from exif metadata'
            self.errors.append({'from':'exif', 'tweetid':0, 'url':'', 'error':err})
           
     
            
            
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
            #Grabs the photo from cloudfront 
            temp_file = os.path.join(self.photo_dir,url.path[1:])
            photo_url = soup.find(attrs={"id": "content"}).find(src=re.compile("cloudfront"))['src']
            urllib.urlretrieve(photo_url , temp_file)
            return [self.exif_extract(temp_file, tweet)] 
        except Exception: 
            err = 'Error trying to download photo'
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
            #Using the normal approach causes a 302 loop because server expects cookies, so....
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
            soup = bs(opener.open(urllib2.Request(url.geturl())))
            temp_file = os.path.join(self.photo_dir,url.path[1:])
            photo_url = soup.find(attrs={"rel": "direct"})['value'] 
            urllib.urlretrieve(photo_url, temp_file)
            return [self.exif_extract(temp_file, tweet)]
        except Exception:
            err = 'Error trying to download photo'
            self.errors.append({'from':'yfrog', 'tweetid':tweet.id, 'url': url.geturl() ,'error':err})
            return []
        
    def imgly(self, url, tweet):
        try:
            soup = bs(urllib.urlopen(url.geturl()))
            temp_file = os.path.join(self.photo_dir,url.path[1:])
            photo_url = "http://img.ly"+soup.find(attrs={"id": "the-image"})['src']
            urllib.urlretrieve(photo_url, temp_file)
            return [self.exif_extract(temp_file, tweet.text)]
        except Exception:
            err = 'Error trying to download photo'
            self.errors.append({'from':'imgly', 'tweetid':tweet.id, 'url': url.geturl() ,'error':err})
            return []
            
    def plixi(self, url, tweet):
        '''
        Handles lockerz.com images also ;)
        '''
        
        api_location ={}
        try:
            
            json_reply= simplejson.load(urllib.urlopen("http://api.plixi.com/api/tpapi.svc/json/photos/"+url.path[3:]))
            if json_reply['Location']['Latitude'] != 0 and json_reply['Location']['Longitude'] != 0:
                api_location['from'] = 'plixi_api'
                api_location['context'] = ('https://twitter.com/%s/status/%s' % (tweet.user.screen_name, tweet.id) , 'Location retrieved from plixi API . \n Tweet was %s \n ' % (tweet.text))
                api_location['latitude'] = json_reply['Location']['Latitude'] 
                api_location['longitude'] = json_reply['Location']['Longitude']
                api_location['time'] = datetime.fromtimestamp(json_reply['UploadDate'])
                api_location['realname'] = tweet.user.name
            else:
                photo_url = json_reply['BigImageUrl']
                temp_file = os.path.join(self.photo_dir, url.path[3:])
                urllib.urlretrieve(photo_url, temp_file)
                api_location = self.exif_extract(temp_file, tweet)
        except Exception:
            err = 'Error getting information from plixi API'
            self.errors.append({'from':'plixi', 'tweetid':tweet.id, 'url': url.geturl() ,'error':err})
        return [api_location]
    
    def twitrpix(self, url, tweet):
        try:
            temp_file = os.path.join(self.photo_dir, url.path[1:])
            photo_url = "http://img.twitrpix.com"+url.path
            urllib.urlretrieve(photo_url, temp_file)
            return [self.exif_extract(temp_file, tweet.text)]
        except Exception:
            err = 'Error trying to download photo'
            self.errors.append({'from':'twitrpix', 'tweetid':tweet.id, 'url': url.geturl() ,'error':err})
            return []
         
    def folext(self, url, tweet):
        try:
            temp_file = os.path.join(self.photo_dir,url.path[1:])
            photo_url = "http://img.folext.com"+url.path+".jpg"    
            urllib.urlretrieve(photo_url, temp_file)
            return [self.exif_extract(temp_file, tweet.text)]
        except Exception:
            err = 'Error trying to download %s ' % (photo_url)
            self.errors.append({'from':'folext', 'tweetid':tweet.id, 'url': url.geturl() ,'error':err})
            return []
        
    def shozu(self, url, tweet):
        try:
            soup = bs(urllib.urlopen(url.geturl()))
            temp_file = os.path.join(self.photo_dir, url.path[3:])
            photo_url = soup.find(attrs={"class": "cls"})['src']
            urllib.urlretrieve(photo_url, temp_file)
            return [self.exif_extract(temp_file, tweet.text)]
        except Exception:
            err = 'Error trying to download photo'
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
        except Exception:
            err = 'Error trying to download photo'
            self.errors.append({'from':'pickhur', 'tweetid':tweet.id, 'url': url.geturl() ,'error':err})
            return []
    
    def moby(self, url, tweet):
        api_loc= {}
        try:
            json_reply = simplejson.load(urllib.urlopen("http://api.mobypicture.com/?t="+url.path[1:]+"&action=getMediaInfo&k="+self.moby_key+"&format=json"))
            if json_reply['post']['location_latlong']:
                api_loc['from'] = "moby_api"
                api_loc['context'] = ('https://twitter.com/%s/status/%s' % (tweet.user.screen_name, tweet.id) , 'Location retrieved from moby.to API .\n Tweet was %s \n ' % (tweet.text))
                api_loc['latitude'] = json_reply['post']['location_latlong'][0]
                api_loc['longitude'] = json_reply['post']['location_latlong'][1]
                api_loc['time'] = datetime.fromtimestamp(json_reply['created_on_epoch'])
                api_loc['realname'] = tweet.user.name
        
            temp_file = os.path.join(self.photo_dir, url.path[1:])
            photo_url = str(json_reply['post']['media']['url_full']).replace('large', 'full')
            urllib.urlretrieve(photo_url, temp_file)
            return [api_loc, self.exif_extract(temp_file, tweet.text)]
        except Exception:
            err = 'Error trying to download photo'
            self.errors.append({'from':'moby', 'tweetid':tweet.id, 'url': url.geturl() ,'error':err})
        return [api_loc]
    
    def twitsnaps(self, url, tweet):
        try:
            temp_file = os.path.join(self.photo_dir, url.path[1:])
            photo_url = "http://twitsnaps.com/snap"+url.path
            urllib.urlretrieve(photo_url, temp_file)
            return [self.exif_extract(temp_file, tweet.text)]
        except Exception:
            err = 'Error trying to download photo'
            self.errors.append({'from':'twitsnaps', 'tweetid':tweet.id, 'url': url.geturl() ,'error':err})
            return []
        
    def twitgoo(self, url, tweet):
        try:
            img_url = bs(urllib.urlopen("http://twitgoo.com/api/message/info"+url.path)).find('imageurl').string
            temp_file = os.path.join(self.photo_dir,url.path[1:])
            urllib.urlretrieve(img_url, temp_file)
            return [self.exif_extract(temp_file, tweet.text)]
        except Exception:
            err = 'Error trying to download photo'
            self.errors.append({'from':'twitgoo', 'tweetid':tweet.id, 'url': url.geturl() ,'error':err})
            return []
    def instagram(self, url, tweet):
        '''
        Handles  instagram links
        
        returns location coordinates
        '''
        try:
            data = {}
            html = urllib.urlopen(url.geturl()).read()
            coordinates = re.findall('center=([-+]?[0-9]*\.[0-9]+|[0-9]+),([-+]?[0-9]*\.[0-9]+|[0-9]+)&', html)
            if coordinates:
                data['from'] = 'Instagram photo'
                data['context'] = ('https://twitter.com/%s/status/%s' % (tweet.user.screen_name, tweet.id) ,'Information retrieved from instagram photo in a tweet. \n Tweet was %s  \n' % (tweet.text))                
                data['time'] = tweet.created_at
                data['longitude'] = float(coordinates[0][1])
                data['latitude'] = float(coordinates[0][0])
                data['realname'] = tweet.user.name
                
            else:
                coordinates = re.findall('sll=([-+]?[0-9]*\.[0-9]+|[0-9]+),([-+]?[0-9]*\.[0-9]+|[0-9]+)&', html)
                if coordinates:
                    data['from'] = 'Instagram photo'
                    data['context'] = ('https://twitter.com/%s/status/%s' % (tweet.user.screen_name, tweet.id) ,'Information retrieved from instagram photo in a tweet. \n Tweet was %s  \n' % (tweet.text))                
                    data['time'] = tweet.created_at
                    data['longitude'] = float(coordinates[0][1])
                    data['latitude'] = float(coordinates[0][0])
                    data['realname'] = tweet.user.name
                    
            return [data] 
        except Exception:
            err = 'Error getting location from instagram photo'
            self.errors.append({'from':'instagram', 'tweetid':tweet.id, 'url':url.geturl(), 'error':err})
            return []
    
    def resolve_url(self, i):
        '''
        Needed to handle the t.co links
        urllib handles redirects automatically so by just opening the url and requesting 
        the current url afterwards we get the target url
        Removing non ascii characters from the links was necessary in some cases, need to investigate more
        '''
        if isinstance(i,unicode):
            i = unicodedata.normalize('NFKD', i).encode('ascii', 'ignore')
        try:
            targeturl = urllib.urlopen(i)
            ret = targeturl.geturl()
        except:
            ret = i
        return ret
            
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
                   'twitgoo.com':self.twitgoo,
                   'gowal.la':self.gowalla,
                   'instagr.am': self.instagram,
                   'lockerz.com' : self.plixi}
        
        final_locations_list=[]
        for i in re.findall("(https?://[\S]+)", tweet.text): 
            url = urlparse(self.resolve_url(i))
            if url.netloc in service:
                try:
                    for loc in service.get(url.netloc, self.default_action)(url, tweet):
                        if loc:
                            final_locations_list.append(loc)
                except Exception, err:
                    self.errors.append({'from':'creepy', 'tweetid':0, 'url':'', 'error':err})
        return (final_locations_list, self.errors)
                           
        
                
        
            
