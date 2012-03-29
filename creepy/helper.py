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
import os.path
import csv
import urllib, simplejson
import datetime
try:
    import cPickle as pickle
except:
    import pickle

class Helper():
    
    def __init__(self):
        pass
    

    def html_escape(self, text):
        """Produce entities within text."""
        html_escape_table = {
                             "&": "&amp;",
                             '"': "&quot;",
                             "'": "&apos;",
                             ">": "&gt;",
                             "<": "&lt;",
                             }
        return "".join(html_escape_table.get(c,c) for c in text)
    def create_kml(self, id, directory, locations): 
        """
        Takes id of a user as input and packs his locations into a kml file
        """  
        #Create the klm file
        # kml is the list to hold all xml attribs. it will be joined in a string later
        kml = []
        kml.append('<?xml version=\"1.0\" encoding=\"UTF-8\"?>')
        kml.append('<kml xmlns=\"http://www.opengis.net/kml/2.2\">') 
        kml.append('<Document>')
        kml.append('  <name>%s.kml</name>' % id)
        for loc in locations:
            desc = '%s Link : %s' % (loc['context'][1], loc['context'][0])
            kml.append('  <Placemark>')
            kml.append('  <name>%s</name>' % loc['time'])
            kml.append('    <description> %s' % self.html_escape(desc))
            kml.append('    </description>') 
            kml.append('    <Point>')
            kml.append('       <coordinates>%s, %s, 0</coordinates>' % (loc['longitude'], loc['latitude']))
            kml.append('    </Point>')
            kml.append('  </Placemark>')
        kml.append('</Document>')
        kml.append('</kml>')
        
        kml_string = '\n'.join(kml)
        try:
            #save the file to disk
            filename = os.path.join(directory, '%s.kml' % id)
            fileobj = open(filename, 'w')
            fileobj.write(kml_string)
            fileobj.close()
            return 'Success'
        except Exception, err:
            return ('Error', err)
    def create_csv(self, id, directory, locations):
        try:
            filename = os.path.join(directory, '%s.csv' % id)
            fileobj = open(filename, 'w')
            writer = csv.writer(fileobj, quoting=csv.QUOTE_ALL)
            writer.writerow(('Time', 'Latitude', 'Longitude', 'Retrieved from', 'Context'))
            for loc in locations:
                writer.writerow( (loc['time'], loc['latitude'], loc['longitude'], loc['from'], '%s Link :%s'% (loc['context'][1], loc['context'][0]) ) )
            fileobj.close()
            return 'Success'
        except Exception, err:
            return ('Error', err)
            
    def remove_duplicates(self, location_list):
        known_timestamps = set()
        processed_results = []
        
        for loc in location_list:
            timestamp = loc['time']
            if timestamp in known_timestamps:
                continue
            else:
                processed_results.append(loc)
                known_timestamps.add(timestamp)
        return processed_results    
    
    def reverse_geocode(self, location):
        '''
        Reverse geocodes a pair of coordinates to an address
        '''
        try:
            url = 'http://maps.googleapis.com/maps/api/geocode/json?latlng=%s,%s&sensor=false'%(location[0], location[1])
            json_reply= simplejson.load(urllib.urlopen(url))
            
            if json_reply['status'] == 'OK':
                address = {}
                address['formatted_address'] = json_reply['results'][0]['formatted_address']
                address['area'] = json_reply['results'][0]['address_components'][0]['short_name']
        except:
            address = 'not_available'
            
        return address
    
    def create_template(self, realname, username, location, loctime, indirectory, outdirectory, fileid):
        information = self.reverse_geocode(location)
        area = information['area']
        formatted_address = information['formatted_address']
        date_struct = datetime.datetime.strptime(loctime, "%Y-%m-%d %H:%M:%S")
        try:
            #read the template
            filename = os.path.join(indirectory, '%s.template' % fileid)
            fileobj = open(filename, 'r+')
            filestring = fileobj.read()
            
            #Replace the placeholders
            filestring = filestring.replace("@formatted_address@", formatted_address).replace("@area@", area).replace("@username@", username).replace("@realname@" ,realname).replace("@date@", date_struct.strftime("%x")).replace("@time@", date_struct.strftime("%X")).replace("@ampm@", date_struct.strftime("%p")).replace("@datetime@", date_struct.strftime("%c")).replace("@month@", date_struct.strftime("%B")).replace("@day@", date_struct.strftime("%A")).replace("@year@", date_struct.strftime("%Y")).replace("@hour@", date_struct.strftime("%H")).replace("@minutes@", date_struct.strftime("%M"))
            
            #write the file to the output directory
            filenameout = os.path.join(outdirectory, '%s.template' % fileid)
            fileobjout = open(filenameout, 'w')
            fileobjout.write(filestring)
            fileobjout.close()
            return 'Success'
        except Exception, err:
            return ('Error', err)
        