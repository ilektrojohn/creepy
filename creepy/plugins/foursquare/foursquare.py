from InputPlugin import InputPlugin
import os
from PyQt4 import QtGui
import foursquare
import logging
import urllib
import datetime
from urlparse import urlparse, parse_qs

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Foursquare(InputPlugin):
    
    name = "foursquare"
    hasWizard = True
    
    def __init__(self):
        self.config, self.options_string = self.readConfiguration("string_options")
        self.api = self.getAuthenticatedAPI()
    
    def getAuthenticatedAPI(self):
        return  foursquare.Foursquare(access_token=self.options_string['hidden_access_token'])     
        
    def isConfigured(self):
        if not self.api:
            self.api = self.getAuthenticatedAPI()
        try:
            self.api.users()
            return (True,"")
        except Exception, err:
            return (False, err.message)
    
    def searchForTargets(self, search_term):
        logger.debug("Attempting to search for targets. Search term was : "+search_term)
        possibleTargets = []
        if not self.api:
            self.api = self.getAuthenticatedAPI()
        params = {"email":search_term,"twitter":search_term,"name":search_term}
        r = self.api.users.search(params=params)
        
        for i in r['results']:
            target = {'pluginName':'Foursquare Plugin'}
            target['targetUserid'] = i['id']
            target['targetUsername'] = i['id']
            target['targetPicture'] = 'profile_pic_%s' % i['id']
            target['targetFullname'] = i['firstName']+" "+i['lastName']
            #save the pic in the temp folder to show it later
            filename = 'profile_pic_%s' % i['id']
            temp_file = os.path.join(os.getcwd(), "temp", filename)
            link = i['photo']['prefix']+"original"+i['photo']['suffix']
            urllib.urlretrieve(link, temp_file)
            possibleTargets.append(target)
        logger.debug(str(len(possibleTargets))+" possible targets were found matching the search query")
        return possibleTargets
   

    def returnLocations(self, target, search_params):
        locations_list = []
        if not self.api:
            self.api = self.getAuthenticatedAPI()
        checkins_list = self.api.users.all_checkins(target['targetUserid'])
        for i in checkins_list:
            if i['type'] == 'venue':
                l = i['venue']['location']
                if l.has_key('lat') and l.has_key['lng']:
                    loc = {}
                    loc['plugin'] = "foursquare"
                    loc['context'] = i['shout'] if i.has_key['shout'] else "No Caption"
                    loc['infowindow'] = self.constructContextInfoWindow(i)                                 
                    loc['date'] = datetime.datetime.fromtimestamp(i['createdAt'])
                    loc['lat'] = l['lat']
                    loc['lon'] = l['lng']
                    loc['shortName'] = i['venue']['name']
                    locations_list.append(loc)
            else:
                if i.has_key['location']:
                    l = i['location']
                    if l.has_key['lat'] and l.has_key['lng']:
                        loc = {}
                        loc['plugin'] = "foursquare"
                        loc['context'] = i['shout'] if i.has_key['shout'] else "No Caption"
                        loc['infowindow'] = self.constructContextInfoWindow(i)                                 
                        loc['date'] = datetime.datetime.fromtimestamp(i['createdAt'])
                        loc['lat'] = l['lat']
                        loc['lon'] = l['lng']
                        loc['shortName'] = l['place'] if l.has_key['place'] else "Not available"
                        locations_list.append(loc)
        logger.debug(len(locations_list)+ " locations have been retrieved")    
        return locations_list
        
    
    
    def runConfigWizard(self):
        try:
            api = foursquare.Foursquare(client_id=self.options_string['hidden_client_id'], client_secret=self.options_string['hidden_client_secret'], redirect_uri=self.options_string['redirect_uri'])
            url = api.oauth.auth_url()
            
            
            
            wizard = QtGui.QWizard()
            page1 = QtGui.QWizardPage()
            
            layout1 = QtGui.QVBoxLayout()
            
            txtArea = QtGui.QTextEdit()
            txtArea.setReadOnly(True)
            txtArea.setText("Please copy the following link to your browser window. \n \n"+
                            url +"\n \n"
                            "Once you authenticate with Foursquare you will be redirected to a link that looks like \n\n"+
                            "https://www.geocreepy.net?code=xxxxxxxxxxxxxxx . \n \n"+
                            "Copy this link to the text box below and click on Finish to complete authorization");
#            label1a = QtGui.QLabel("Click next to connect to instagram.com . Please login with your account in order to authorize creepy")
            inputLink = QtGui.QLineEdit()
            inputLink.setObjectName("inputLink")
            labelLink = QtGui.QLabel("Link from browser:")
            '''
            html = QtWebKit.QWebView()
            html.load(QtCore.QUrl(url))
            html.urlChanged.connect(self.urlChanged)
            layout1.addWidget(label1a)
            layout2.addWidget(html)
            '''
            layout1.addWidget(txtArea)
            layout1.addWidget(labelLink)
            layout1.addWidget(inputLink)
            page1.setLayout(layout1)
            wizard.addPage(page1)
            wizard.resize(600,400)
            if wizard.exec_():
                c = self.parseRedirectUrl(str(inputLink.text()))
                print c
                if c:
                    try:
                        access_token = api.oauth.get_token(c)
                        
                        self.options_string['hidden_access_token'] = access_token
                        self.config.write()
                    except Exception, err:
                        self.showWarning("Error Getting Access Token", "Please verify that the link you pasted was correct. Try running the wizard again.")
                else:
                    self.showWarning("Error Getting Access Token", "Please verify that the link you pasted was correct. Try running the wizard again.")
            
        except Exception,err:
            logger.exception(err)
    
    def parseRedirectUrl(self, link):
        try:
            return parse_qs(urlparse(link).query)['code'][0]
        except Exception, err:
            logger.error(err)
            return None
        
    def showWarning(self, title, text):
        QtGui.QMessageBox.warning(self, title, text)   
        
    def constructContextInfoWindow(self, photo):
        html = self.options_string['infowindow_html']
        caption = photo.caption.text if photo.caption else "No Caption"
        return html.replace("@TEXT@",caption).replace("@DATE@",photo.created_time.strftime("%a %b %d,%H:%M:%S %z")).replace("@PLUGIN@", "instagram").replace("@LINK@", photo.link)