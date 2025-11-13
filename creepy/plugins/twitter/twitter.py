#!/usr/bin/python
# -*- coding: utf-8 -*-

from models.InputPlugin import InputPlugin
import tweepy
import logging
import os
import urllib
import pytz
from PyQt4.QtGui import QWizard, QWizardPage, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt4.QtCore import QUrl
from PyQt4.QtWebKit import QWebView
from tweepy import Cursor
from datetime import datetime
from dominate.tags import *
from collections import Counter
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


class Twitter(InputPlugin):
    name = 'twitter'
    hasWizard = True
    hasLocationBasedMode = True
    hasRateLimitInfo = True

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
        self.options_boolean = self.readConfiguration('boolean_options')[1]
        self.api = None
        self.wizard = QWizard()

    def searchForTargets(self, search_term):
        possibleTargets = []
        logger.debug('Searching for Targets from Twitter Plugin. Search term is : ' + search_term)
        try:
            if self.api is None:
                self.api = self.getAuthenticatedAPI()
            search_results = self.api.search_users(q=search_term)
            if search_results:
                logger.debug('Twitter returned  ' + str(len(search_results)) + ' results')
                for i in search_results:
                    if self.options_boolean['exclude_geo_disabled'] == 'True' and not i.geo_enabled:
                        continue
                    target = {'pluginName': 'Twitter Plugin'}
                    target['targetUserid'] = i.id_str
                    target['targetUsername'] = i.screen_name
                    target['targetPicture'] = 'profile_pic_%s' % i.id_str
                    target['targetFullname'] = i.name
                    # save the pic in the temp folder to show it later
                    filename = 'profile_pic_%s' % i.id_str
                    temp_file = os.path.join(GeneralUtilities.getTempDir(), filename)
                    # Retieve and save the profile phot only if it does not exist
                    if not os.path.exists(temp_file):
                        urllib.urlretrieve(i.profile_image_url, temp_file)
                    possibleTargets.append(target)
        except tweepy.TweepError, e:
            logger.error('Error authenticating with Twitter API.')
            logger.error(e)
            if e.response.status_code == 429:
                remaining, limit, reset = self.getRateLimitStatus('search_users')
                return False, 'Error authenticating with Twitter: {0}. Your limits will be renewed at : {1}'.format(
                    e.message, reset.strftime('%Y-%m-%d %H:%M:%S %z'))
            return False, 'Error authenticating with Twitter: {0}'.format(e.message)
        except Exception, err:
            logger.error(err)
            logger.error('Error searching for targets in Twitter plugin.')
        return possibleTargets

    def getAuthenticatedAPI(self):
        try:
            auth = tweepy.auth.OAuthHandler(self.options_string['hidden_application_key'],
                                            self.options_string['hidden_application_secret'])
            auth.set_access_token(self.options_string['hidden_access_token'],
                                  self.options_string['hidden_access_token_secret'])
            return tweepy.API(auth)
        except Exception, e:
            logger.error(e)
            return None

    def runConfigWizard(self):
        try:
            oAuthHandler = tweepy.OAuthHandler(self.options_string['hidden_application_key'],
                                               self.options_string['hidden_application_secret'])
            authorizationURL = oAuthHandler.get_authorization_url(True)

            self.wizard.setWindowTitle('Twitter plugin configuration wizard')
            page1 = QWizardPage()
            page2 = QWizardPage()
            layout1 = QVBoxLayout()
            layout2 = QVBoxLayout()
            layoutInputPin = QHBoxLayout()

            label1a = QLabel(
                'Click next to connect to twitter.com . Please login with your account and follow the instructions in '
                'order to authorize creepy')
            label2a = QLabel(
                'Copy the PIN that you will receive once you authorize cree.py in the field below and click finish')
            pinLabel = QLabel('PIN')
            inputPin = QLineEdit()
            inputPin.setObjectName('inputPin')

            analysisHtml = QWebView()
            analysisHtml.load(QUrl(authorizationURL))

            layout1.addWidget(label1a)
            layout2.addWidget(analysisHtml)
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
                    oAuthHandler.get_access_token(str(self.wizard.field('inputPin').toString()).strip())
                    self.options_string['hidden_access_token'] = oAuthHandler.access_token
                    self.options_string['hidden_access_token_secret'] = oAuthHandler.access_token_secret
                    self.saveConfiguration(self.config)
                except Exception, err:
                    logger.error(err)
                    self.showWarning('Error completing the wizard',
                                     'We were unable to obtain the access token for your account, please try to run '
                                     'the wizard again. Error was {0}'.format(err.message))

        except Exception, err:
            logger.error(err)
            self.showWarning('Error completing the wizard', 'Error was: {0}'.format(err.message))

    def showWarning(self, title, text):
        try:
            QMessageBox.warning(self.wizard, title, text, None)
        except Exception, err:
            logger.error(err)

    def getAuthorizationURL(self):
        """
        :return:  the authorization URL for Twitter or None if there was an exception
        """
        try:
            if not self.options_string:
                self.options_string = self.readConfiguration('string_options')[1]
            oAuthHandler = tweepy.OAuthHandler(self.options_string['hidden_application_key'],
                                               self.options_string['hidden_application_secret'])
            authorizationURL = oAuthHandler.get_authorization_url(True)
            return authorizationURL
        except Exception, err:
            logger.error(err)
            return None

    def isConfigured(self):
        """
        :return: a tuple. The first element is True or False, depending if the plugin is configured or not. The second
        element contains an optional message for the user
        """
        try:
            if not self.options_string:
                self.options_string = self.readConfiguration('string_options')[1]
            if self.api is None:
                oAuthHandler = tweepy.OAuthHandler(self.options_string['hidden_application_key'],
                                                   self.options_string['hidden_application_secret'])
                oAuthHandler.set_access_token(self.options_string['hidden_access_token'],
                                              self.options_string['hidden_access_token_secret'])
                self.api = tweepy.API(oAuthHandler)
            logger.debug(self.api.me().name)
            return True, ''
        except tweepy.TweepError, e:
            logger.error('Error authenticating with Twitter API.')
            logger.error(e)
            return False, 'Error authenticating with Twitter. ' + e.message
        except Exception, e:
            logger.error('Error authenticating with Twitter API.')
            logger.error(e)
            return False, 'Error authenticating with Twitter. ' + e.message

    def returnAnalysis(self, target, search_params):
        """

        :param target:
        :param search_params:
        :return:
        """
        conversionResult = False
        formalTimezoneName = ''
        locations_list = []
        twitterDiv = div(id='twitter')
        twitterDiv += h2('Twitter profile information')
        incl_rts = search_params['boolean']['include_retweets']
        excl_rpls = search_params['boolean']['exclude_replies']
        if not self.api:
            self.api = self.getAuthenticatedAPI()
        try:
            logger.debug('Attempting to retrieve profile information for ' + target['targetUsername'])
            userObject = self.api.get_user(user_id=target['targetUserid'])
            twitterDiv += p('Account was created on {0}'.format(userObject.created_at.strftime('%Y-%m-%d %H:%M:%S %z')))
            if userObject.statuses_count:
                twitterDiv += p(
                    'The user has tweeted {0} times ( including retweets ).'.format(str(userObject.statuses_count)))
            if userObject.name:
                twitterDiv += p(u'Self-reported real name: {0}'.format(userObject.name))
            if userObject.description:
                twitterDiv += p(u'Description: {0}'.format(userObject.description))
            if userObject.location:
                twitterDiv += p(u'Self-reported location: {0}'.format(userObject.location))
            if userObject.time_zone:
                conversionResult, formalTimezoneName = self.getTimezoneNameFromReported(userObject.time_zone)
                if conversionResult:
                    twitterDiv += p(u'Self-reported time zone: {0}'.format(formalTimezoneName))
                else:
                    twitterDiv += p(u'Self-reported time zone: {0}'.format(userObject.time_zone))
            if userObject.geo_enabled:
                twitterDiv += p('User has enabled the possibility to geolocate their tweets.')
            else:
                twitterDiv += p('User has disabled the possibility to geolocate their tweets.')
            if userObject.followers_count:
                twitterDiv += p('The user has {0} followers.'.format(str(userObject.followers_count)))
            if userObject.friends_count:
                twitterDiv += p('The user is following {0} users.'.format(str(userObject.friends_count)))
            if userObject.listed_count:
                twitterDiv += p('The user is listed in {0} public lists.'.format(str(userObject.listed_count)))

            logger.debug('Attempting to retrieve the tweets for user ' + target['targetUsername'])
            tweets = Cursor(self.api.user_timeline, count=100, user_id=target['targetUserid'],
                            exclude_replies=excl_rpls, include_rts=incl_rts).items()
            timestamps = []
            repliedTo = []
            retweeted = []
            clientApplications = []
            mentioned = []
            hashtags = []
            for j in tweets:
                finalDateTimeObj = pytz.utc.localize(j.created_at)
                if conversionResult:
                    createdUtcTimezone = pytz.utc.localize(j.created_at)
                    try:
                        userTimezone = pytz.timezone(formalTimezoneName)
                        createdUserTimezone = userTimezone.normalize(createdUtcTimezone.astimezone(userTimezone))
                        timestamps.append(createdUserTimezone)
                        finalDateTimeObj = createdUserTimezone
                    except Exception:
                        finalDateTimeObj = createdUtcTimezone
                        timestamps.append(createdUtcTimezone)
                else:
                    timestamps.append(pytz.utc.localize(j.created_at))
                if j.in_reply_to_screen_name:
                    repliedTo.append(j.in_reply_to_screen_name)
                if hasattr(j, 'retweeted_status'):
                    retweeted.append(j.retweeted_status.user.name)
                if j.source:
                    clientApplications.append(j.source)
                if j.entities:
                    if hasattr(j, 'entities.user_mentions'):
                        for mention in j.entities.user_mentions:
                            mentioned.append(mention.screen_name)
                    if hasattr(j, 'hashtags'):
                        for hashtag in j.entities.hashtags:
                            hashtags.append(hashtag.text)
                loc = self.buildLocationFromTweet(j, finalDateTimeObj)
                if loc:
                    locations_list.append(loc)

            logger.debug('{0} locations were retrieved from Twitter Plugin'.format(len(locations_list)))
            if len(repliedTo) > 0:
                twitterDiv += p('User has replied to the following users : ')
                repliedToTable = self.createFrequencyTableFromCounter(Counter(repliedTo), 'User screen name',
                                                                      'repliedToTable', 10)
                twitterDiv += repliedToTable
            if len(retweeted) > 0:
                twitterDiv += p('User has retweeted the following users : ')
                retweetedTable = self.createFrequencyTableFromCounter(Counter(retweeted), 'User screen name',
                                                                      'retweetedTable', 10)
                twitterDiv += retweetedTable
            if len(mentioned) > 0:
                twitterDiv += p('User has mentioned the following users : ')
                mentionedTable = self.createFrequencyTableFromCounter(Counter(mentioned), 'User screen name',
                                                                      'mentionedTable', 10)
                twitterDiv += mentionedTable
            if len(clientApplications) > 0:
                twitterDiv += p('User has been using the following clients : ')
                clientApplicationsTable = self.createFrequencyTableFromCounter(Counter(clientApplications),
                                                                               'Client Application',
                                                                               'clientApplicationsTable', 10)
                twitterDiv += clientApplicationsTable
            if len(hashtags) > 0:
                twitterDiv += p('User has used the following hashtags : ')
                hashtagsTable = self.createFrequencyTableFromCounter(Counter(hashtags), 'Hashtag', 'hashtagsTable', 10)
                twitterDiv += hashtagsTable
            if len(timestamps) > 0:
                twitterDiv += p('User tweets time frequency: ')
                hourPeriodsTable = self.createFrequencyTableFromList(self.getTimeChunksFrequency(timestamps, 8),
                                                                     'Hour Period', 'hourPeriodsTable')
                twitterDiv += hourPeriodsTable
                twitterDiv += p('User has been twitting at the following times : ')
                hoursTable = self.createFrequencyTableFromCounter(Counter([d.hour for d in timestamps]), 'Hour',
                                                                  'hoursTable', 24)
                twitterDiv += hoursTable
        except tweepy.TweepError, e:
            logger.error('Error authenticating with Twitter API.')
            logger.error(e)
            if e.response.status_code == 429:
                remaining, limit, reset = self.getRateLimitStatus('user_timeline')
                logger.error(
                    'Error getting locations from twitter plugin: {0}. Your limits will be renewed at : {1}'.format(
                        e.message, reset.strftime('%Y-%m-%d %H:%M:%S %z')))
        except Exception, e:
            logger.error(e)
            logger.error('Error getting locations from twitter plugin')
        return locations_list, twitterDiv

    def searchForResultsNearPlace(self, geocode):
        locations_list = []
        logger.debug('Attempting to retrieve tweets around {0}'.format(geocode))
        try:
            if self.api is None:
                self.api = self.getAuthenticatedAPI()
            # Min Radius is 1km, convert m to km and set it to 1km if it is less than that
            if not geocode.split(',')[2].endswith('km'):
                if int(geocode.split(',')[2].replace('m', '')) < 1000:
                    geocode = ','.join(geocode.split(',')[:2]) + ',1km'
                else:
                    radius = int(geocode.split(',')[2].replace('m', '')) / 1000
                    geocode = ','.join(geocode.split(',')[:2]) + ',{0}km'.format(radius)

            tweets = Cursor(self.api.search, count=100, q='*', geocode=geocode, result_type='recent').items()
            for tweet in tweets:
                finalDateTimeObj = pytz.utc.localize(tweet.created_at)
                loc = self.buildLocationFromTweet(tweet, finalDateTimeObj)
                if loc:
                    locations_list.append(loc)
        except tweepy.TweepError, e:
            logger.error('Error authenticating with Twitter API.')
            logger.error(e)
            if e.response.status_code == 429:
                remaining, limit, reset = self.getRateLimitStatus('search_near_location')
                logger.error(
                    'Error getting locations from twitter plugin: {0}. Your limits will be renewed at : {1}'.format(
                        e.message, reset.strftime('%Y-%m-%d %H:%M:%S %z')))
        except Exception, e:
            logger.error(e)
            logger.error('Error getting locations from twitter plugin')
        return locations_list

    def getRateLimitStatus(self, query):
        try:
            if self.api is None:
                self.api = self.getAuthenticatedAPI()
            reply = self.api.rate_limit_status()
            if query == 'search_users':
                return reply['resources']['users']['/users/search']['remaining'], \
                       reply['resources']['users']['/users/search']['limit'], \
                       datetime.fromtimestamp(reply['resources']['users']['/users/search']['reset'])
            elif query == 'search_near_location':
                return reply['resources']['search']['/search/tweets']['remaining'], \
                       reply['resources']['search']['/search/tweets']['limit'], \
                       datetime.fromtimestamp(reply['resources']['search']['/search/tweets']['reset'])
            elif query == 'user_timeline':
                return reply['resources']['statuses']['/statuses/user_timeline']['remaining'], \
                       reply['resources']['statuses']['/statuses/user_timeline']['limit'], \
                       datetime.fromtimestamp(reply['resources']['statuses']['/statuses/user_timeline']['reset'])
            elif query == 'all':
                return reply['resources']['users']['/users/search'], reply['resources']['search']['/search/tweets'], \
                       reply['resources']['statuses']['/statuses/user_timeline']
        except Exception, e:
            logger.error(e)
            logger.error('Error getting rate limit status from twitter plugin')

    def buildLocationFromTweet(self, tweet, finalDateTimeObj):
        """
        First Handle the coordinates return field
        Twitter API returns GeoJSON, see http://www.geojson.org/geojson-spec.html for the spec
        We don't handle MultiPoint, LineString, MultiLineString, MultiPolygon and Geometry Collection
        """
        loc = {}
        loc['plugin'] = 'twitter'
        loc['username'] = tweet.user.screen_name
        loc['context'] = tweet.text
        loc['date'] = finalDateTimeObj
        loc['infowindow'] = self.constructContextInfoWindow(tweet, finalDateTimeObj)
        if tweet.coordinates and tweet.place:
            if tweet.coordinates['type'] == 'Point':
                loc['lat'] = tweet.coordinates['coordinates'][1]
                loc['lon'] = tweet.coordinates['coordinates'][0]
                loc['shortName'] = tweet.place.name
                loc['accuracy'] = 'high'
            elif tweet.coordinates.type == 'PolyGon':
                c = self.getCenterOfPolygon(tweet.coordinates['coordinates'])
                loc['lat'] = c[1]
                loc['lon'] = c[0]
                loc['shortName'] = tweet.place.name
                loc['accuracy'] = 'low'
            return loc
        elif tweet.place and not tweet.coordinates:
            if tweet.place.bounding_box.type == 'Point':
                loc['lat'] = tweet.place.bounding_box.coordinates[1]
                loc['lon'] = tweet.place.bounding_box.coordinates[0]
                loc['shortName'] = tweet.place.name
                loc['accuracy'] = 'high'
            elif tweet.place.bounding_box.type == 'Polygon':
                c = self.getCenterOfPolygon(tweet.place.bounding_box.coordinates[0])
                loc['lat'] = c[1]
                loc['lon'] = c[0]
                loc['shortName'] = tweet.place.name
                loc['accuracy'] = 'low'
            return loc
        else:
            return {}

    def getTimeChunksFrequency(self, timestamps, chunkSize):
        hourFreq = Counter([d.hour for d in timestamps])
        hourPeriods = self.sliceLinkedList(range(24), chunkSize)
        hourPeriodTotals = []
        for hPeriod in hourPeriods:
            totalTweets = 0
            for hour in hPeriod:
                totalTweets += hourFreq[hour]
            hourPeriodTotals.append(('{0}-{1}'.format(str(hPeriod[0]), str(hPeriod[-1])), totalTweets))
        hourPeriodTotals.sort(key=lambda x: x[1], reverse=True)
        return hourPeriodTotals

    def createFrequencyTableFromList(self, lst, objectName, tableName):
        objectTable = table(id=tableName, cls='pure-table pure-table-bordered')
        head = thead()
        head.add(th(objectName))
        head.add(th('Count'))
        objectTable.add(head)
        objectTable.add(tbody())
        for item in lst:
            row = tr()
            row.add(td(item[0]))
            row.add(td(item[1]))
            objectTable.add(row)
        return objectTable

    def createFrequencyTableFromCounter(self, counter, objectName, tableName, itemsCount):
        objectTable = table(id=tableName, cls='pure-table pure-table-bordered')
        head = thead()
        head.add(th(objectName))
        head.add(th('Count'))
        objectTable.add(head)
        objectTable.add(tbody())
        for item in counter.most_common(itemsCount):
            row = tr()
            row.add(td(item[0]))
            row.add(td(item[1]))
            objectTable.add(row)
        return objectTable

    def constructContextInfoWindow(self, tweet, finalDateTimeObj):
        html = unicode(self.options_string['infowindow_html'])
        # returned value also becomes unicode since tweet.text is unicode, and carries the encoding also
        return html.replace('@TEXT@', tweet.text). \
            replace('@DATE@', finalDateTimeObj.strftime('%Y-%m-%d %H:%M:%S %z')). \
            replace('@PLUGIN@', u'twitter').replace('@USERNAME@', tweet.user.screen_name). \
            replace('@LINK@', 'https://twitter.com/statuses/{0}'.format(tweet.id_str))

    def getCenterOfPolygon(self, coord):
        """
        We need to get the "center" of the polygon. Accuracy is not a major aspect here since
        we originally got a polygon, so there was not much accuracy to start with. We convert the 
        polygon to a rectangle by selecting 4 points : 
        a) Point with the Lowest latitude
        b) Point with the Highest Latitude
        c) Point with the Lowest Longitude
        d) Point with the Highest Longitude
        
        and then get the center of this rectangle as the point to draw on the map
        """
        lat_list = []
        lon_list = []
        for j in coord:
            lon_list.append(j[0])
            lat_list.append(j[1])
        lon_list.sort()
        lat_list.sort()
        lat = float(lat_list[0]) + ((float(lat_list[len(lat_list) - 1]) - float(lat_list[0])) / 2)
        lon = float(lon_list[0]) + ((float(lon_list[len(lon_list) - 1]) - float(lon_list[0])) / 2)
        return lon, lat

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

    def sliceLinkedList(self, lst, chunkSize):
        n = len(lst)
        for i in range(n):
            d = n - chunkSize - i
            if d > 0:
                yield lst[i:i + chunkSize:1]
            else:
                yield lst[i:] + lst[:-d]

    def getTimezoneNameFromReported(self, tzReported):
        allTimezones = pytz.all_timezones
        for timezone in allTimezones:
            if tzReported.lower() in timezone.lower():
                return True, timezone
        return False, tzReported
