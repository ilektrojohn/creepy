#!/usr/bin/python
# -*- coding: utf-8 -*-
from os.path import expanduser
import webbrowser
from math import radians, cos, sin, asin, sqrt

    
def getUserHome():
    return expanduser("~")

def reportProblem():
    webbrowser.open_new_tab('https://github.com/ilektrojohn/creepy/issues')
    
def calcDistance(lat1, lng1, lat2, lng2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Original Code from Mickael Dunn <Michael.Dunn@mpi.nl> 
    on http://stackoverflow.com/a/4913653/983244
    """
    # convert decimal degrees to radians 
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])

    # haversine formula 
    dlng = lng2 - lng1 
    dlat = lat2 - lat1 
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    c = 2 * asin(sqrt(a)) 

    # 6378100 m is the mean radius of the Earth
    meters = 6378100 * c
    return meters     

def html_escape(text):
        html_escape_table = {
                             "&": "&amp;",
                             '"': "&quot;",
                             "'": "&apos;",
                             ">": "&gt;",
                             "<": "&lt;",
                             }
        return "".join(html_escape_table.get(c, c) for c in text)