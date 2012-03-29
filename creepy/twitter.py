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
from time import gmtime, strftime
import os.path
try:
    import cPickle as pickle
except:
    import pickle
import simplejson
import urllib
import urlanalyzer
import base64
import multiprocessing
import dateutil.relativedelta as rl
from datetime import datetime
import time

g_conf_file = None
g_urlanalyzer = None

class Twitter():
    """
    Handles oAuth and all twitter related functions
    
    Provides all the functionality needed in regards of accessing twitter via 
    it's API
    """
    def __init__(self, conf_file , auth = True):
        #Do some "magic" so twitter guys are happy :)
        global g_conf_file 
        global g_urlanalyzer
        g_conf_file = conf_file
        self.profilepics_dir = conf_file['directories']['profilepics_dir']
        self.cache_dir = conf_file['directories']['cache_dir']
        self.urlanalyzer = urlanalyzer.URLAnalyzer(conf_file['directories']['img_dir'], conf_file['misc']['moby_key'])
        g_urlanalyzer = urlanalyzer.URLAnalyzer(conf_file['directories']['img_dir'], conf_file['misc']['moby_key'])
        self.tweepy_count = conf_file['tweepy']['count']
        self.handle_links = conf_file['twitter']['handle_links']
        if auth:
            cons_string = conf_file['twitter_auth']['cons_string']
            cons_key, cons_secret = base64.b64decode(cons_string).split(",")
            acc_key = conf_file['twitter_auth']['access_key']
            acc_secret = conf_file['twitter_auth']['access_secret']
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
            for i in Cursor(self.api.user_timeline, screen_name=username, count=self.tweepy_count).items():
                timeline.append(i)
    
        except tweepy.TweepError, err:
            conn_err = {'from':'twitter_connection', 'tweetid':'', 'url': 'twitter' ,'error':err.reason}
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
        Utilizes the geonames.com service.Not very accurate when the location is not very specific
        
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
            data['context'] = ('https://twitter.com/%s/status/%s' % (tweet.user.screen_name, tweet.id) , 'Information retrieved from twitter. \n Tweet was : %s \n ' % (tweet.text))
            data['time'] = tweet.created_at
            data['latitude'] = tweet.coordinates['coordinates'][1]
            data['longitude'] = tweet.coordinates['coordinates'][0]
            data['realname'] = tweet.user.name
        elif tweet.geo is not None:
            data['from'] = 'twitter' 
            data['context'] = ('https://twitter.com/%s/status/%s' % (tweet.user.screen_name, tweet.id) , 'Information retrieved from twitter.. \n Tweet was : %s \n ' % (tweet.text))
            data['time'] = tweet.created_at 
            data['latitude'] = tweet.geo['coordinates'][0]
            data['longitude'] = tweet.geo['coordinates'][1]
            data['realname'] = tweet.user.name
        elif tweet.place is not None:
            name = tweet.place['full_name']
            c = self.get_location_fromplace(name)
            if c:
                data['from'] = 'twitter_place' 
                data['context'] = ('https://twitter.com/%s/status/%s' % (tweet.user.screen_name, tweet.id) , 'Information retrieved from twitter place using GeoNames service. \n Tweet was : %s \n ' % (tweet.text))
                data['time'] = tweet.created_at 
                data['latitude'] = c[0]
                data['longitude'] = c[1]
                data['realname'] = tweet.user.name
            else :
                a = tweet.place['bounding_box']['coordinates']
                data['from'] = 'twitter_bounding_box'
                data['context'] = ('https://twitter.com/%s/status/%s' % (tweet.user.screen_name, tweet.id) , 'Information retrieved from twitter bounding box. Really NOT accurate. \n Tweet was : %s \n ' % (tweet.text))
                data['time'] = tweet.created_at 
                data['latitude'] = a[0][0][1]
                data['longitude'] = a[0][0][0]
                data['realname'] = tweet.user.name
        return data
    
    
        
    def get_tweets_locations(self, tweets):
        """
        Wrapper function for location information retrieval.
        
        Returns a tuple containing a list of location dictionaries retrieved from the analysis of a list of tweets
        and a list of errors from the process
        """
        location = []
        errors = []
        
        tasks = multiprocessing.Queue()
        results = multiprocessing.Queue()
        
        num = multiprocessing.cpu_count() * 2
        analyzers = [Analyzer(tasks, results) for i in xrange(num)]
        
        for a in analyzers:
            a.start()
            
        num_of_jobs = len(tweets)
        for i in xrange(num_of_jobs):
            tasks.put(Task(tweets[i]))
        
        for i in xrange(num):
            tasks.put(None)
        
        while num_of_jobs:
            result = results.get()
            if result:
                if (isinstance(result, list)):
                    location.extend(result)
                elif (isinstance(result,dict)):
                    location.append(result)
            num_of_jobs -= 1
        return (location, errors)
 
    def get_tweets(self, username):
        identifier_tweet ='tweets_'+username
        #Check to see if we have saved tweets and locations for the current user
        saved_tweets = self.unpickle_data(identifier_tweet)
        if saved_tweets:
            latest_id = saved_tweets['latest_id']
            oldest_id = saved_tweets['oldest_id']
            latest, err = self.get_latest_tweets(username, latest_id)
            if len(latest):
                latest_id = latest[0].id
            older, err2 = self.get_older_tweets(username, oldest_id)
            if len(older):
                oldest_id = older[-1].id
            conn_err = dict(err, **err2)
            tweets = latest+older
            tweets = self.sort_tweet_list(tweets)
            num_of_tweets = saved_tweets['total']+len(latest)+len(older)   
        else:
            tweets, conn_err = self.get_all_tweets(username)
            num_of_tweets = len(tweets)
            if len(tweets) > 0:
                latest_id = tweets[0].id
                oldest_id = tweets[-1].id
            
        if len(tweets) > 0:
            try:
                #add the latest and the oldest tweet we retrieved as pointers
                cached_data = {'latest_id':latest_id, 'oldest_id':oldest_id, 'total':num_of_tweets}
                self.pickle_data(cached_data, identifier_tweet)
             
            except Exception, err:
                print 'Exception ',err
        #We need to return only the newly retrieved tweets, the rest have been analyzed already and their locations
        #are in the location cache
        return (tweets, conn_err)
    
    def get_locations(self, tweets, username):
        identifier_loc ='locations_'+username
        identifier_errors ='errors_'+username
        results_params = {}
        #Check to see if we have saved tweets and locations for the current user
        locations_old = self.unpickle_data(identifier_loc)
        locations, errors = self.get_tweets_locations(tweets)
        if locations_old:
            locations = locations+locations_old    
        results_params['locations'] = len(locations)
        results_params['tweets'] = len(tweets)
        try:
            #I just love it :) Go figure what it does.
            cached_tweets = [tweet for tweet in tweets if tweet.id in [er['tweetid'] for er in errors]]
            #tweets for which we had some errors analyzing locations from them
            cached_errors = {'tweets':cached_tweets}
            self.pickle_data(cached_errors, identifier_errors)
            self.pickle_data(locations, identifier_loc)
         
        except Exception, err:
            print 'Exception ',err
   
        return (locations, results_params)

class Analyzer(multiprocessing.Process):
    def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
            
    def run(self):
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                break
            res = next_task()
            self.result_queue.put(res)
        return
        
class Task(object):
    def __init__(self, tweet):
        self.tweet = tweet
    def __call__(self):
        try:
            t = Twitter(g_conf_file, False)
            loc = t.get_status_location(self.tweet)
            if not loc and self.handle_links == 'yes':
                loc = g_urlanalyzer.get_photo_location(self.tweet)
            return loc
        except:
            return []
    
    
    
    