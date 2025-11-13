#!/usr/bin/python
# -*- coding: utf-8 -*-
import hashlib


class Location(object):
    def __init__(self, plugin=None, username=None, datetime=None, longitude=0, latitude=0, context=None, shortName=None,
                 longName=None, streetNumber=None, route=None, locality=None, postalCode=None, country=None,
                 visible=True, media_url=None, accuracy='low'):
        if datetime and longitude and latitude and plugin:
            self.id = hashlib.sha1(datetime.isoformat() + str(longitude) + str(latitude) + str(plugin)).hexdigest()
        self.plugin = plugin
        self.username = username
        self.datetime = datetime
        self.longitude = longitude
        self.latitude = latitude
        self.context = context
        self.shortName = shortName
        self.longName = longName
        self.streetNumber = streetNumber
        self.route = route
        self.locality = locality
        self.postalCode = postalCode
        self.country = country
        self.visible = visible
        self.media_url = media_url
        self.accuracy = accuracy

    def updateId(self):
        self.id = hashlib.sha1(
            self.datetime.isoformat() + str(self.longitude) + str(self.latitude) + self.username.encode(
                'utf-8')).hexdigest()
