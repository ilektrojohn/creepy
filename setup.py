from distutils.core import setup
import py2exe, sys, os

sys.argv.append('py2exe')

includes = ["sip",
            "distutils",
            "PyQt4.QtNetwork",
            "tweepy",
            "flickrapi",
            "instagram",
            "googleapiclient.discovery",
            "oauth2client.client",
            "dateutil.parser",
            "dbhash"]

DATA = [
    ('imageformats', ['C:\\Users/ikakavas/.virtualenvs/creepy/Lib/site-packages/PyQt4/plugins/imageformats/qjpeg4.dll',
                      'C:\\Users/ikakavas/.virtualenvs/creepy/Lib/site-packages/PyQt4/plugins/imageformats/qgif4.dll',
                      'C:\\Users/ikakavas/.virtualenvs/creepy/Lib/site-packages/PyQt4/plugins/imageformats/qico4.dll',
                      'C:\\Users/ikakavas/.virtualenvs/creepy/Lib/site-packages/PyQt4/plugins/imageformats/qmng4.dll',
                      'C:\\Users/ikakavas/.virtualenvs/creepy/Lib/site-packages/PyQt4/plugins/imageformats/qsvg4.dll',
                      'C:\\Users/ikakavas/.virtualenvs/creepy/Lib/site-packages/PyQt4/plugins/imageformats/qtiff4.dll'
    ]
    ),
    'include/cacerts.txt'
]

setup(
    name='creepy',
    version='1.2',
    author='Yiannis Kakavas',
    author_email='jkakavas@gmail.com',
    options={
    "py2exe": {
    "includes": includes
    }
    },
    windows=[{'script': "CreepyMain.py", 'icon_resource': [(1, "include/creepy.ico")]}],
    zipfile=None,
    data_files=DATA,
)