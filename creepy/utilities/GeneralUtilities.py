#!/usr/bin/python
# -*- coding: utf-8 -*-
from os.path import expanduser
import webbrowser
import os
import errno
from math import radians, cos, sin, asin, sqrt


def getUserHome():
    return expanduser("~")


def getIncludeDir():
    """ Provide path to include directory.  Change this for installed packages """
    incdir = os.path.join(os.getcwdu(), 'include')
    if os.path.isdir(incdir):
        return incdir
    else:
        return '/usr/share/creepy/include'


def getLogDir():
    logdir = expanduser('~/.creepy')
    try:
        os.makedirs(logdir)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(logdir):
            pass
        else:
            raise
    return logdir


def getProjectsDir():
    if os.path.exists('/usr/share/creepy'):
        directory = os.path.join(expanduser('~/.creepy'), 'projects')
    else:
        directory = os.path.join(os.getcwd(), 'projects')
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(directory):
            pass
        else:
            raise
    return directory

def getTempDir():
    if os.path.exists('/usr/share/creepy'):
        directory = os.path.join(expanduser('~/.creepy'), 'temp')
    else:
        directory = os.path.join(os.getcwd(), 'temp')
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(directory):
            pass
        else:
            raise
    return directory

def getLocalPluginDir(pluginname):
    if os.path.exists('/usr/share/creepy/plugins'):
        localplugindir = expanduser(os.path.join('~/.creepy/plugins', pluginname))
        try:
            os.makedirs(localplugindir)
        except OSError as e:
            if e.errno == errno.EEXIST and os.path.isdir(localplugindir):
                pass
            else:
                raise
        return localplugindir
    else:
        return [os.path.join(os.getcwd(), 'plugins')]

def getPluginDirs():
    if os.path.exists('/usr/share/creepy/plugins'):
        # if creepy is installed via debian package
        return [os.path.join(os.getcwd(), 'plugins'),
                '/usr/share/creepy/plugins',
                '~/.creepy/plugins']
    else:
        return [os.path.join(os.getcwd(), 'plugins')]


def reportProblem():
    webbrowser.open_new_tab('https://github.com/jkakavas/creepy/issues')


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

