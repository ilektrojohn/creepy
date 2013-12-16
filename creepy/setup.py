from distutils.core import setup
import py2exe

# Now you need to pass arguments to setup
# windows is a list of scripts that have their own UI and
# thus don't need to run in a console.

setup(windows=['CreepyMain.py'],
      options={

# And now, configure py2exe by passing more options;

          'py2exe': {

# This is magic: if you don't add these, your .exe may
# or may not work on older/newer versions of windows.

              "dll_excludes": [
                  "MSVCP90.dll",
                  "MSWSOCK.dll",
                  "mswsock.dll",
                  "powrprof.dll",
                  ],

# Py2exe will not figure out that you need these on its own.
# You may need one, the other, or both.

              'includes': [
                  'sip',
                  'PyQt4.QtNetwork',
                  ],
          }
      },

# Qt's dynamically loaded plugins and py2exe really don't
# get along.

data_files = [
            ('imageplugins', [
            'c:\Python27\lib\site-packages\PyQt4\plugins\imageformats\qgif4.dll',
            'c:\Python27\lib\site-packages\PyQt4\plugins\imageformats\qjpeg4.dll',
            'c:\Python27\lib\site-packages\PyQt4\plugins\imageformats\qsvg4.dll',
            ]),
],
)