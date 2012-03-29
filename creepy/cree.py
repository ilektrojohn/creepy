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

import flickr
import twitter
import helper

class Cree():
    """
    The controller class for the creepy application.
    
    Cree is called from the GUI and acts as a wrapper for various functions that the GUI class
    is not accessing directly. Configuration file is passed to Cree on instantiation and is used 
    in order to be passed to various modules that need access to configuration values.
    
    """
    def __init__(self, conf_file):
        self.f= flickr.Flickr(conf_file)
        self.t = twitter.Twitter(conf_file)
        
    def get_tweets(self, twittername):
        tweets, conn_err = self.t.get_tweets(twittername)
        return (tweets, conn_err)
    
    
    def get_locations(self, twittername, tweets,  flickrid):
        """ Wrapper for the process of determining a users location through the
            accessible modules. 
            
            Returns a tuple containing a list of location dictionaries, and a 
            dictionary of parameters
        """
        hel = helper.Helper()
        location_list = []
        twitparams = {}
        flickrparams={}
        if twittername != '':
            twitlocs, twitparams = self.t.get_locations(tweets, twittername)
            if twitlocs:
                location_list.extend(twitlocs)
        if flickrid != '':
            flickrlocs, flickrparams = self.f.return_locations(flickrid)
            if flickrlocs:
                location_list.extend(flickrlocs)
        params = dict(twitparams, **flickrparams)
        return (hel.remove_duplicates(location_list), params)

    def search_for_users(self, service, query, param=''):
        """
        Wrapper function for the search process from the accessible modules
        
        Returns a list of users that match the search query
        """
        
        if service == 'twitter':
            users = self.t.search_user(query)
        elif service == 'flickr':
            if param == 'username':
                users = self.f.search_user(query)
            elif param == 'realname':
                users = self.f.search_real_name(query)
        return users
            