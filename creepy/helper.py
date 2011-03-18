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
    def create_kml(self, id, dir, locations): 
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
            filename = os.path.join(dir, '%s.kml' % id)
            fileobj = open(filename, 'w')
            fileobj.write(kml_string)
            fileobj.close()
            return 'Success'
        except Exception, err:
            return ('Error', err)
    def create_csv(self, id, dir, locations):
        try:
            filename = os.path.join(dir, '%s.csv' % id)
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