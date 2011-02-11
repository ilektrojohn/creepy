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

import tweepy
from tweepy import Cursor
import os.path
try:
    import cPickle as pickle
except:
    import pickle
import simplejson
import urllib
import urlanalyzer


class Twitter():
    """
    Handles oAuth and all twitter related functions
    
    Provides all the functionality needed in regards of accessing twitter via 
    it's API
    """
    def __init__(self, conf_file):
        cons_key = conf_file['twitter_auth']['consumer_key'] 
        cons_secret = conf_file['twitter_auth']['consumer_secret'] 
        acc_key = conf_file['twitter_auth']['access_key']
        acc_secret = conf_file['twitter_auth']['access_secret']
        self.profilepics_dir = conf_file['directories']['profilepics_dir']
        self.cache_dir = conf_file['directories']['cache_dir']
        self.urlanalyzer = urlanalyzer.URLAnalyzer(conf_file['directories']['img_dir'], conf_file['misc']['moby_key'])

        if cons_key and cons_secret and acc_key and acc_secret:
            auth = tweepy.OAuthHandler(cons_key, cons_secret)
            auth.set_access_token(acc_key, acc_secret)
            self.api = tweepy.API(auth)
            self.authed = True
        else:
            self.authed = False
            self.api = tweepy.API()
        
    def authorize_for_twitter(self, key, secret):
        """
        Returns the authorization URL that the user needs to follow
        in order to 'sign in with twitter'
        """
	auth = tweepy.OAuthHandler(key, secret)
        url = auth.get_authorization_url(True)
       	return (auth, url)
        
    def search_user(self, name):
        """
        BAsic search functionality
        
        Returns a list of users, and saves their profile pics in a
        temporary location
        """
        users = []
        if self.authed:
            users = self.api.search_users(name)
            for user in users:
                try:
                    filename = 'profile_pic_%s' % user.screen_name
                    temp_file = os.path.join(self.profilepics_dir, filename)
                    urllib.urlretrieve(user.profile_image_url, temp_file)
                except Exception, err:
                    pass
                    #print 'Error retrieving %s profile picture' % (user.screen_name), err
            return users
        else:
            users.append('auth_error')
            return users
        
    def pickle_data(self, data, identifier):
        """
        Serializes data
        """
        filename = 'creepy_%s.pcl' % (identifier)
        file = open(os.path.join(self.cache_dir, filename), 'w')
        pickle.dump(data, file)
        file.close()
    
    def unpickle_data(self, identifier):
        """
        Unserializes data
        """
        filename = 'creepy_%s.pcl' % (identifier)
        if os.path.exists(os.path.join(self.cache_dir, filename)):
            file = open(os.path.join(self.cache_dir, filename), 'r')
            try:
                data = pickle.load(file)
                return data
            except Exception, err:
                #print 'Malformed data, or file does not exist .Error :',err
                return
        else :
            return None
        
    def sort_tweet_list(self, tweet_list):
        """
        Sort a list of tweets based on their ID. The latest tweets get first
        
        Returns a list of sorted tweets
        """
        tweets = sorted(tweet_list, key = lambda tweet: tweet.id, reverse=True)    
        return tweets
    
    def get_all_tweets(self, username):
        """
        Try and retrieve all user's tweets. If not possible, returns all the so far retrieved
        
        Returns a list of retrieved tweets
        """
        timeline=[]
        conn_err = {}
        try:
            for i in Cursor(self.api.user_timeline, screen_name=username, count=200).items():
                timeline.append(i)
    
        except tweepy.TweepError, err:
            conn_err = {'from':'twitter_connection', 'tweetid':'', 'url': 'twitter' ,'error':err}
            #print 'Connection to twitter failed with error :', err
        return (timeline, conn_err)
    
    def get_older_tweets(self, username, oldest_id):
        """
        Retrieve tweets that are older than the one with oldest_id
        """
        older=[]
        conn_err = {}
        try:
            for i in Cursor(self.api.user_timeline, screen_name=username, max_id=oldest_id).items():
                older.append(i)
        except tweepy.TweepError, err:
            conn_err = {'from':'twitter_connection', 'tweetid':'', 'url': 'twitter' ,'error':err}
            #print 'Connection to twitter failed with error :', err
        return (older, conn_err)
        
    def get_latest_tweets(self, username, latest_id):
        """
        Retrieve all tweets that were posted sooner than the one with the latest_id
        """
        latest=[]
        conn_err = {}
        try:
            for i in Cursor(self.api.user_timeline, screen_name=username, since_id=latest_id).items():
                latest.append(i)
        except tweepy.TweepError, err:
            #print 'Connection to twitter failed with error :', err
            conn_err = {'from':'twitter_connection', 'tweetid':'', 'url': 'twitter' ,'error':err}
        return (latest, conn_err)
    
    def get_location_fromplace(self, name):
        """
        Gets location in form of coordinates pair from a lexicographic representation of a place.
        Utilizes the geonames.com service.Not very accurate when the location is bot very specific
        
        Returns a tuple with the location coordinates
        """
        places = self.unpickle_data('places')
        if not places:
            places = {}
        if unicode(name) in places:
            return places[unicode(name)]
        else:
            try:
                params = urllib.urlencode({'q':unicode(name).encode('utf-8'), 'maxRows':1, 'username':'creepy'})
                json = simplejson.load(urllib.urlopen("http://api.geonames.org/searchJSON?%s" % params))
                if 'geonames' in json and json['totalResultsCount'] > 0:
                    places[unicode(name)] = [json['geonames'][0]['lat'], json['geonames'][0]['lng']]
                    self.pickle_data(places, 'places')
                    return [json['geonames'][0]['lat'], json['geonames'][0]['lng']]
                else: return
            except Exception, err:
                #print "error getting info from geonames ", err
                return
        
         
    def get_status_location(self, tweet):
        """
        Tries to determine the location by the information provided from the twitter API
        
        Returns a location dictionary
        """
        data = {}
        if tweet.coordinates:
            data['from'] = 'twitter' 
            data['context'] = 'Information retrieved from twitter. \n Tweet was : %s ' % (tweet.text)
            data['time'] = tweet.created_at
            data['latitude'] = tweet.coordinates['coordinates'][1]
            data['longitude'] = tweet.coordinates['coordinates'][0]
        elif tweet.geo is not None:
            data['from'] = 'twitter' 
            data['context'] = 'Information retrieved from twitter.. \n Tweet was : %s ' % (tweet.text)
            data['time'] = tweet.created_at 
            data['latitude'] = tweet.geo['coordinates'][0]
            data['longitude'] = tweet.geo['coordinates'][1]
        elif tweet.place is not None:
            name = tweet.place['full_name']
            c = self.get_location_fromplace(name)
            if c:
                data['from'] = 'twitter_place' 
                data['context'] = 'Information retrieved from twitter place using GeoNames service. \n Tweet was : %s ' % (tweet.text)
                data['time'] = tweet.created_at 
                data['latitude'] = c[0]
                data['longitude'] = c[1]
            else :
                a = tweet.place['bounding_box']['coordinates']
                data['from'] = 'twitter_bounding_box' 
                data['context'] = 'Information retrieved from twitter bounding box. Really NOT accurate. \n Tweet was : %s ' % (tweet.text)
                data['time'] = tweet.created_at 
                data['latitude'] = a[0][0][1]
                data['longitude'] = a[0][0][0]
        return data
    def get_tweets_locations(self, tweets):
        """
        Wrapper function for location information retrieval.
        
        Returns a tuple containing a list of location dictionaries retrieved from the analysis of a list of tweets
        and a list of errors from the process
        """
        location = []
        errors = []
        for tweet in tweets:
            print 'looking for locations in tweet nr %s' % tweet.id
            loc1 = self.get_status_location(tweet)
            if loc1:    
                location.append(loc1)
            loc2, errors = self.urlanalyzer.get_photo_location(tweet)
            if loc2:
                location.extend(loc2)
            print 'done'
        return (location, errors)
        
             
    def get_twitter_locations(self, username):
        """
        Wrapper function for retrieving a user's locations
        
        Returns a list of location dictionaries for a specific user
        
        """ 
        identifier_tweet ='tweets_'+username
        identifier_loc ='locations_'+username
        print 'getting tweets'
        results_params = {}
        #Check to see if we have saved tweets and locations for the current user
        tweets_old = self.unpickle_data(identifier_tweet)
        if tweets_old:
            print 'had old tweets'
            latest_id = tweets_old['latest_id']
            oldest_id = tweets_old['oldest_id']
            latest, err = self.get_latest_tweets(username, latest_id)
            print 'finished new tweets'
            if len(latest) > 0:
                latest_id = latest[0].id
            older, err2 = self.get_older_tweets(username, oldest_id)
            print 'finished old tweets'
            if len(older):
                oldest_id = older[-1].id
            conn_err = dict(err, **err2)
            tweets = latest+older+tweets_old['tweets']
            tweets = self.sort_tweet_list(tweets)
            results_params['tweets'] = tweets_old['total']+len(latest)+len(older)
            locations_old = self.unpickle_data(identifier_loc)
            print 'trying to get locations'
            locations_new, errors = self.get_tweets_locations(tweets)
            print 'got locations'
            locations = locations_old+locations_new    
        else:
            tweets, conn_err = self.get_all_tweets(username)
            print 'received tweets'
            locations, errors = self.get_tweets_locations(tweets)
            print 'received locations' 
            if len(tweets) > 0:
                latest_id = tweets[0].id
                oldest_id = tweets[-1].id
            results_params['tweets'] = len(tweets)
            
        print 'received tweets'
        if conn_err:
            errors.append(conn_err)
            
        results_params['locations'] = len(locations)
        results_params['errors'] = errors
        
        
        
        #Introducing a threshold for saving the tweets and locations
        if len(tweets) > 0:
            results_params['tweets_count'] = tweets[0].user.statuses_count
            try:
                #I just love it :) Go figure what it does.
                cached_tweets = [tweet for tweet in tweets if tweet.id in [er['tweetid'] for er in errors]]
                #add the latest and the oldest tweet we retrieved as pointers
                cached_data = {'latest_id':latest_id, 'oldest_id':oldest_id, 'tweets':cached_tweets, 'total':results_params['tweets']}
                self.pickle_data(cached_data, identifier_tweet)
                self.pickle_data(locations, identifier_loc)
             
            except Exception, err:
                print 'Exception ',err
        else:
            results_params['tweets_count'] = 0
        return (locations, results_params)
      
        
    
    
    
    
