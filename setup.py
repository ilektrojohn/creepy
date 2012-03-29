import sys

from itertools import chain
from os.path import join, dirname
from setuptools import setup, find_packages

__version__ = '0.2'
package_name = 'creepy'
# used to specify that a feature should depend on the presence
# of another feature
intra_dependency = '%s[%%s]==%s' % (package_name, __version__)

def read(name, *args):
    try:
        with open(join(dirname(__file__), name)) as read_obj:
            return read_obj.read(*args)
    except Exception:
        return ''

def test_and_add_imports(module, requirement, requirements, feature, link):
    """
    used to test for the presence of modules already present in the
    python path. For example, those installed via yum or apt-get
    """
    try:
        __import__(module)
    except ImportError:
        print >> sys.stderr, ('%s not found, try download packages '
                              'from: %s' % (module, link))
        requirements[feature].append(requirement)


# this supports people installing the specific features of creepy they
# need, without the need to bring in all the third-party requirements
extras_require = {
    'flickr': [
        'flickrapi==1.4.2',
        ],
    'twitter': [
        'tweepy==1.7.1',
    ],

    'exif': [],
    'map': [
        intra_dependency % 'flickr',
        intra_dependency % 'twitter',
    ],

}

# not on pypi:
test_and_add_imports('pyexiv2', 'pyexiv2==0.3.0', extras_require, 'exif',
                     'http://tilloy.net/dev/pyexiv2/download.html')
# not on pypi
# apt-get install libosmgpsmap-dev python-osmgpsmap
test_and_add_imports('osmgpsmap', 'osmgpsmap==0.7.2', extras_require, 'map',
                     'http://nzjrs.github.com/osm-gps-map/')
# not installable via distutils, available on ubuntu with:
# apt-get install python-gtk (or python-gtk2)
test_and_add_imports('gtk.gdk', 'PyGTK==2.12.1', extras_require, 'map',
                     'http://www.pygtk.org/downloads.html')
# not installable via distutils, available on ubuntu with:
# apt-get install python-gobject
test_and_add_imports('gobject', 'PyGObject==2.10.1', extras_require, 'map',
                     'http://www.pygtk.org/downloads.html')

all_unique_packages = set(list(chain(*extras_require.values())))

extras_require['all'] = list(all_unique_packages)

# baseline requirements that the core functionality requires
install_requires = [
    'configobj==4.7.2',
    'BeautifulSoup==3.2.0',
    'simplejson==2.2.1',
]

# in case additional setup needs to be done on different versions of python
extra_setup = {}

setup(
    name=package_name,
    version=__version__,
    description='An OSINT geolocation aggregator. Offers geolocation '
                'information gathering through social networking platforms',
    long_description=read('README'),
    # packaging by Rob Dennis <rdennis@gmail.com>
    author='Ioannis Kakavas',
    author_email=' jkakavas@gmail.com',
    url='https://github.com/ilektrojohn/creepy/',
    install_requires=install_requires,
    extras_require=extras_require,
    packages=find_packages(exclude=['ez_setup']),
    classifiers=[
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Topic :: Security',
    ],
    **extra_setup
)
