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



from threading import Thread
import cree
import gobject
import gtk.gdk
import os
import osmgpsmap
from tweepy import OAuthHandler as oauth
import webbrowser
from configobj import ConfigObj
import shutil


gobject.threads_init()
gtk.gdk.threads_init()


class CreepyUI(gtk.Window):
    """
    The main GUI class
    
    Provides all the GUI functionality for creepy. 
    """

    def __init__(self):
        self.CONF_DIR = os.path.join(os.path.expanduser('~'), '.creepy')

        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)

        self.set_default_size(800, 600)
        self.connect('destroy', lambda x: gtk.main_quit())
        self.set_title('Cree.py location creeper')
        
	#If it is the first time creepy is run copy the config file and necessary images to .creepy
	if not os.path.exists(self.CONF_DIR):
	    os.mkdir(self.CONF_DIR)
            shutil.copy('/usr/share/pyshared/creepy/include/creepy.conf', os.path.join(self.CONF_DIR, 'creepy.conf'))
	    shutil.copy('/usr/share/pyshared/creepy/include/evil_twitter.png', os.path.join(self.CONF_DIR, 'evil_twitter.png'))
	    shutil.copy('/usr/share/pyshared/creepy/include/flickr.png', os.path.join(self.CONF_DIR, 'flickr.png'))
	    shutil.copy('/usr/share/pyshared/creepy/include/index.png', os.path.join(self.CONF_DIR, 'index.png'))
	    shutil.copy('/usr/share/pyshared/creepy/include/default.jpg', os.path.join(self.CONF_DIR, 'default.jpg'))	 
	    #create the temp folders
            os.makedirs(os.path.join(self.CONF_DIR, 'cache'))
	    os.makedirs(os.path.join(self.CONF_DIR, 'images'))
            os.makedirs(os.path.join(self.CONF_DIR, 'images', 'profilepics'))  
            #write to the initial configuration file
            config_file = os.path.join(self.CONF_DIR, 'creepy.conf')
            tmp_conf = ConfigObj(infile=config_file)
            tmp_conf.create_empty=True
            tmp_conf.write_empty_values=True 
            tmp_conf['directories']['img_dir'] = os.path.join(self.CONF_DIR, 'images')
            tmp_conf['directories']['cache_dir'] = os.path.join(self.CONF_DIR, 'cache')
            tmp_conf['directories']['profilepics_dir'] = os.path.join(self.CONF_DIR, 'images', 'profilepics')
            tmp_conf.write()
	
        #Try to load the options file
        try:
            config_file = os.path.join(self.CONF_DIR, 'creepy.conf')
            self.config = ConfigObj(infile=config_file)
            self.config.create_empty=True
            self.config.write_empty_values=True
            self.set_auth(self.config)
            self.profilepics_dir = self.config['directories']['profilepics_dir']
            
        except Exception, err:
            text = 'Error parsing configuration file : %s' % err
            self.create_dialog('Error', text)
            
            
        #check if dirs for temp data exist and if not try to create them
        if not os.path.exists(self.config['directories']['img_dir']):
            self.create_directory(self.config['directories']['img_dir'])
        if not os.path.exists(self.config['directories']['profilepics_dir']):
            self.create_directory(self.config['directories']['profilepics_dir'])
        if not os.path.exists(self.config['directories']['cache_dir']):
            self.create_directory(self.config['directories']['cache_dir'])
        
        #Create an outer Vbox to include everything
        outer_box = gtk.VBox(False, 0)
        self.add(outer_box)
        #Create a menu bar
        mb = gtk.MenuBar()
        filemenu = gtk.Menu()
        file = gtk.MenuItem("File")
        file.set_submenu(filemenu)
        
        exit = gtk.MenuItem("Exit")
        exit.connect("activate", gtk.main_quit)
        filemenu.append(exit)
        
        mb.append(file)
        menubox = gtk.VBox(False, 2)
        menubox.pack_start(mb, False, False, 0)
        outer_box.pack_start(menubox, False, False, 0)
        
        # Creates the notebook layout
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        outer_box.pack_start(notebook)
        
        #Creates the Map overview tab and adds it to the notebook
        tab1 = gtk.VBox(False, 0)
        label1 = gtk.Label("Map View")
        notebook.append_page(tab1, label1)
        
        #Load the map
        self.osm = osmgpsmap.GpsMap()
        self.osm.layer_add(
                    osmgpsmap.GpsMapOsd(
                        show_dpad=True,
                        show_zoom=True))
        
        #connect keyboard shortcuts for the map
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_FULLSCREEN, gtk.gdk.keyval_from_name("F11"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_UP, gtk.gdk.keyval_from_name("Up"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_DOWN, gtk.gdk.keyval_from_name("Down"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_LEFT, gtk.gdk.keyval_from_name("Left"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_RIGHT, gtk.gdk.keyval_from_name("Right"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_ZOOMIN , gtk.gdk.keyval_from_name("KP_Add"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_ZOOMOUT, gtk.gdk.keyval_from_name("KP_Subtract"))
        
        self.osm.connect('button_release_event', self.map_clicked)

        #Create a table for map and locations list
        maploc = gtk.Table(5, 5, True)
        tab1.pack_start(maploc)
        loclist_label = gtk.Label("Locations List")   
        self.loc_list = gtk.VBox(False, 8)
        self.loc_list.add(loclist_label)
    
        maploc.attach(self.loc_list, 0, 2, 0, 5)
        self.update_location_list([])
        maploc.attach(self.osm, 2, 5, 0, 5)

        self.textview = gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)
        info = gtk.ScrolledWindow()
        info.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        info.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        info.add(self.textview)
        
        #Create the horizontal box that holds the buttons and the buttons themselves
        hbox = gtk.HBox(False, 0)
        self.show_button = gtk.Button('Search for target')
        self.show_button.connect('clicked', self.thread_show_clicked)
       
        
        hbox.pack_start(self.show_button, True, False, 0)
       

        tab1.pack_end(info, False)
        tab1.pack_end(hbox, False)

        
        #Create the targets tab
        tab2 = gtk.VBox(False, 0)
        label2 = gtk.Label('Targets')
        notebook.append_page(tab2, label2)
        
        #Create a table to hold all stuff here
        search_table = gtk.Table(20, 10, True)
        t_label0 = gtk.Label('Selected Targets')
        twitter_target_label = gtk.Label('Twitter Username')
        self.twitter_target = gtk.Entry()
        flickr_target_label = gtk.Label('Flickr UserID')
        self.flickr_target = gtk.Entry()
        
        
        self.twitter_username = gtk.Entry()
        t_label1 = gtk.Label('Search for:')
        search_twitter_button = gtk.Button('Search')
        search_twitter_button.connect('clicked', self.thread_search_twitter)
        clear_twitter_button = gtk.Button('Clear')
        clear_twitter_button.connect('clicked', self.clear_twitter_list)
        twitter_im = gtk.Image()
        pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(self.CONF_DIR, 'evil_twitter.png'))
        scaled_buf = pixbuf.scale_simple(50,50,gtk.gdk.INTERP_BILINEAR)
        twitter_im.set_from_pixbuf(scaled_buf)
        

        self.twitter_list = gtk.VBox(False, 0)
        search_table.attach(t_label0, 0, 2, 0, 1)
        search_table.attach(twitter_target_label, 0, 2, 1, 2)
        search_table.attach(self.twitter_target, 2, 4 , 1, 2)
        search_table.attach(flickr_target_label, 4, 6, 1, 2)
        search_table.attach(self.flickr_target, 7, 9, 1, 2)
        search_table.attach(twitter_im, 0, 1, 2, 4)
        search_table.attach(t_label1, 0, 1, 4, 5)
        search_table.attach(self.twitter_username, 1, 4, 4, 5)
        search_table.attach(search_twitter_button, 5, 7, 4, 5)
        search_table.attach(clear_twitter_button, 8, 10, 4, 5)
        search_table.attach(self.twitter_list, 0, 10, 5, 10)
        self.update_twitterusername_list([])
        
        #add flickr search
        flickr_im = gtk.Image()
        pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(self.CONF_DIR, 'flickr.png'))
        scaled_buf = pixbuf.scale_simple(50,50,gtk.gdk.INTERP_BILINEAR)
        flickr_im.set_from_pixbuf(scaled_buf)
        

        self.flickr_list = gtk.VBox(False, 0)
        t_label2 = gtk.Label('Search for:')
        self.flickr_username = gtk.Entry()
        search_flickr_button = gtk.Button('Search')
        search_flickr_button.connect('clicked', self.thread_search_flickr)
        search_flickrreal_button = gtk.Button('Search for real name')
        search_flickrreal_button.connect('clicked', self.thread_search_flickr_realname)
        clear_flickr_button = gtk.Button('Clear')
        clear_flickr_button.connect('clicked', self.clear_flickr_list)
        #search_table.attach(t_label_twitter, 2, 4, 3, 4)
        search_table.attach(flickr_im, 0, 1, 10, 12)
        search_table.attach(t_label2, 0, 1, 12, 13)
        search_table.attach(self.flickr_username, 1, 4, 12, 13)
        search_table.attach(search_flickr_button, 4, 5, 12, 13)
        search_table.attach(search_flickrreal_button, 5, 8, 12, 13)
        search_table.attach(clear_flickr_button, 8, 10, 12, 13)

        
        search_table.attach(self.flickr_list, 0, 10, 13, 18)
        self.update_flickrusername_list([])
        
        tab2.pack_start(search_table)
        
        #Create the settings tab
        tab3 = gtk.VBox(False, 0)
        label3 = gtk.Label('Settings')
        notebook.append_page(tab3, label3)
        
        self.settings_table = gtk.Table(20, 10, True)
        twit_label = gtk.Label('Twitter')
        self.settings_table.attach(twit_label, 0, 1, 0, 1)
        
        
        
        self.twitbox = gtk.HBox(False, 0)
        #If creepy is already authorized, hide the option
        if self.config['twitter_auth']['access_key'] !='' and self.config['twitter_auth']['access_secret'] != '':
            self.set_twit_options(authorized=True)
        else:
            self.set_twit_options(authorized=False)
            
        flickr_options = gtk.HBox(False, 0)
        flabel = gtk.Label('Flickr')
        flickr_key_label = gtk.Label('Flickr API key')
        self.flickr_key = gtk.Entry()
        if self.config['flickr']['api_key'] != '':
            self.flickr_key.set_text(self.config['flickr']['api_key'])
        flickr_key_button = gtk.Button('Save')
        flickr_key_button.connect('clicked', self.save_flickr_config)
        flickr_options.pack_start(flickr_key_label, False, False, 5)
        flickr_options.pack_start(self.flickr_key, 20)
        flickr_options.pack_end(flickr_key_button, False, False, 2)
        
        
        dir_label = gtk.Label('Photo locations')
        img_options = gtk.HBox(False, 0)
        prof_options = gtk.HBox(False, 0)
        img_options_label = gtk.Label('Path for temporarily saved images')
        prof_options_label = gtk.Label('Path for saved profile pictures')
        self.img_options_entry = gtk.Entry()
        self.prof_options_entry = gtk.Entry()
        self.img_options_entry.set_text(self.config['directories']['img_dir'])
        self.prof_options_entry.set_text(self.config['directories']['profilepics_dir'])
        img_options_button = gtk.Button('Save')
        img_options_button.connect('clicked', self.save_img_options)
        prof_options_button = gtk.Button('Save')
        prof_options_button.connect('clicked', self.save_prof_options)
        img_options.pack_start(img_options_label, False, False, 5)
        img_options.pack_start(self.img_options_entry, True, True, 10)
        img_options.pack_end(img_options_button, False, False, 5)
        prof_options.pack_start(prof_options_label, False, False, 5)
        prof_options.pack_start(self.prof_options_entry, True, True, 10)
        prof_options.pack_end(prof_options_button, False, False, 5)
        clear_cache_button = gtk.Button('Clear photos cache')
        clear_cache_button.connect('clicked', self.clear_photo_cache)
        
        self.settings_table.attach(flabel, 0, 1, 3, 4)
        self.settings_table.attach(flickr_options, 0, 10, 4, 5)
        
        self.settings_table.attach(dir_label, 0, 2, 6, 7)
        self.settings_table.attach(img_options, 0, 10, 7, 8)
        self.settings_table.attach(prof_options, 0, 10, 8, 9)
        self.settings_table.attach(clear_cache_button, 8,10, 9, 10)
        
        tab3.pack_start(self.settings_table)
        
    
    
    def clear_photo_cache(self, button):
        folders = (self.config['directories']['img_dir'], self.config['directories']['profilepics_dir'])
        for folder in folders:
            for the_file in os.listdir(folder):
                file_path = os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception, err:
                    self.create_dialog('Error ', 'Error deleting folders, please do it manually')
        text = 'Contents of folder %s were successfully deleted' % folder
        self.create_dialog('Success', text)
        
    def save_img_options(self, button):
        self.config['directories']['img_dir'] = self.img_options_entry.get_text()
        self.config.write()
        self.create_dialog('Success', 'Changes successfully saved')
    def save_prof_options(self, button):
        self.config['directories']['profilepics_dir'] = self.prof_options_entry.get_text()
        self.config.write()
        self.create_dialog('Success', 'Changes successfully saved')
    def save_flickr_config(self, button):
        self.config['flickr']['api_key'] = self.flickr_key.get_text()
        self.config.write()
        self.create_dialog('Success', 'Flickr API key successfully saved')
    def set_twit_options(self, authorized):
        if self.twitbox:
            for i in self.twitbox.get_children():
                self.twitbox.remove(i)
        else:
            self.twitbox = gtk.HBox(False, 0)
        
        if authorized == False :   
            auth_button = gtk.Button('Authorize Creepy')
            auth_button.set_tooltip_text('Clicking this will open your browser to access twitter and get an authorization pin')
            auth_button.connect('clicked', self.button_authorize_twitter)
            self.auth_pin = gtk.Entry()
            auth_pin_label = gtk.Label('Pin :')
            self.auth_finalize_button = gtk.Button('OK')
            self.auth_finalize_button.set_sensitive(0)
            self.auth_pin.connect('changed', self.set_button_active)
            self.auth_finalize_button.connect('clicked', self.fin_authorize_twitter)
        
            self.twitbox.pack_start(auth_button, False, False, 0)
            self.twitbox.pack_end(self.auth_finalize_button, False, False, 5)
            self.twitbox.pack_end(self.auth_pin, False, False, 20)
            self.twitbox.pack_end(auth_pin_label, False, False, 20)
            self.settings_table.attach(self.twitbox, 0, 10, 1, 2)
            self.settings_table.show_all()

        else:
            authorized_label = gtk.Label('Creepy is already authorized for Twitter.')
            reset_button = gtk.Button('reset auth settings')
            reset_button.connect('clicked', self.reset_auth_settings)
            self.twitbox.pack_start(authorized_label, False, False, 0)
            self.twitbox.pack_end(reset_button, False, False, 0)
            self.settings_table.attach(self.twitbox, 0, 10, 1, 2)
            self.settings_table.show_all()
            
    def set_auth(self, conf_file):    
        self.creepy = cree.Cree(conf_file)   
        
    def reset_auth_settings(self, button):
        self.config['twitter_auth']['access_key'] = ''
        self.config['twitter_auth']['access_secret'] = ''
        self.config.write()    
        self.settings_table.remove(self.twitbox)
        self.set_twit_options(authorized=False)
      
    def set_button_active(self, button):
        self.auth_finalize_button.set_sensitive(1)
        
    def button_authorize_twitter(self, button):
        self.oauth = oauth(self.config['twitter_auth']['consumer_key'], self.config['twitter_auth']['consumer_secret'])
        url = self.oauth.get_authorization_url(True)
        webbrowser.open(url)
    
    def fin_authorize_twitter(self, button):
        verif = self.auth_pin.get_text().strip()
        try:
            self.oauth.get_access_token(verif)
            message = 'Authentication successful'
            key = self.oauth.access_token.key
            secret = self.oauth.access_token.secret
            self.config['twitter_auth']['access_key'] = key
            self.config['twitter_auth']['access_secret'] = secret
            self.config.write()
            self.settings_table.remove(self.twitbox)
            self.set_twit_options(authorized=True)
            self.set_auth(self.config)
        except Exception, err:
            message = "Authentication failed with error %s" % (err)
        dialog = gtk.MessageDialog(
                                   parent         = None,
                                   flags          = gtk.DIALOG_DESTROY_WITH_PARENT,
                                   type           = gtk.MESSAGE_INFO,
                                   buttons        = gtk.BUTTONS_OK,
                                   message_format = message)
        dialog.set_title('Twitter authentication')
        dialog.connect('response', lambda dialog, response: dialog.destroy())
        dialog.show()
        
        
    def search_twitter(self, username):
        users = self.creepy.search_for_users('twitter', username)
        if len(users) == 0 :
            self.create_dialog('Error', 'No results for the search query')
        elif users[0] == 'auth_error':
            self.create_dialog('Error', 'Only authenticated users can search for users. Check your settings')
        else:
            gobject.idle_add(self.update_twitterusername_list, users)
    
    def thread_search_twitter(self, button):
        username = self.twitter_username.get_text()
        if username:
            Thread(target=lambda : self.search_twitter(username)).start()
        else :
            self.create_dialog('error', 'Did you forget something ?? \n The search query maybe ??')
    def search_flickr(self, username):
        users = self.creepy.search_for_users('flickr', username, 'username')
        if len(users) == 0 :
            self.create_dialog('Error', 'No results for the search query')
        else:
            gobject.idle_add(self.update_flickrusername_list, users)
    
    def thread_search_flickr(self, button):   
        name = self.flickr_username.get_text()
        if name:
            Thread(target=lambda : self.search_flickr(name)).start()
        else :
            self.create_dialog('error', 'Did you forget something ?? \n The search query maybe ??')
    def search_flickr_realname(self, name):
        users = self.creepy.search_for_users('flickr', name, 'realname')
        if len(users) == 0 :
            self.create_dialog('Error', 'No results for the search query')
        else:
            gobject.idle_add(self.update_flickrusername_list, users)
       
        
    def thread_search_flickr_realname(self, button):
        name = self.flickr_username.get_text()
        if name:
            Thread(target=lambda : self.search_flickr_realname(name)).start()
        else :
            self.create_dialog('error', 'Did you forget something ?? \n The search query maybe ??')
    def select_target(self, button):
        username = self.twitter_username.get_text()
        
    def clear_flickr_list(self, button):    
        self.update_flickrusername_list([])
        
    def clear_twitter_list(self, button):
        self.update_twitterusername_list([])
    def update_twitterusername_list(self,  users):
        for child in self.twitter_list.get_children():
            self.twitter_list.remove(child)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        self.twitter_list.pack_start(sw, True, True, 0)
        store = self.twitterusername_list_model(users)
        
        treeView = gtk.TreeView(store)
        treeView.connect("row-activated", self.twitter_set_target)
        treeView.set_rules_hint(True)
        sw.add(treeView)
        
        self.twitterusername_columns(treeView)
        self.show_all()
    
    def twitterusername_list_model(self, users):
        store = gtk.ListStore(str, str, str, gtk.gdk.Pixbuf)
        if users:
            for user in users:
                file = '%sprofile_pic_%s' % (self.profilepics_dir, user.screen_name)
                profile_pic = gtk.gdk.pixbuf_new_from_file(file)
                store.append([str(user.id), str(user.screen_name), str(user.name), profile_pic])
        return store
    
    def twitterusername_columns(self, treeView):
        
        rendererText1 = gtk.CellRendererText()
        col0 = gtk.TreeViewColumn("Screen Name")
        col0.pack_start(rendererText1, True)
        col0.set_attributes(rendererText1, text=1)
        col0.set_sort_column_id(0)
        treeView.append_column(col0)
        
        rendererText2 = gtk.CellRendererText()
        col1 = gtk.TreeViewColumn("Full Name")
        col1.pack_start(rendererText2, True)
        col1.set_attributes(rendererText2, text=2)
        col1.set_sort_column_id(1)
        treeView.append_column(col1)
        
        rendererImage = gtk.CellRendererPixbuf()
        col2 = gtk.TreeViewColumn("Photo")
        col2.pack_start(rendererImage, True)
        col2.set_attributes(rendererImage, pixbuf=3)
        treeView.append_column(col2)
    
    def twitter_set_target(self, widget, row, col):
        model = widget.get_model()  
        self.twitter_target.set_text(model[row][1])
        
        
    def update_flickrusername_list(self,  users):
        for child in self.flickr_list.get_children():
            self.flickr_list.remove(child)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        self.flickr_list.pack_start(sw, True, True, 0)
        store = self.flickrusername_list_model(users)
        
        treeView = gtk.TreeView(store)
        treeView.connect("row-activated", self.flickr_set_target)
        treeView.set_rules_hint(True)
        sw.add(treeView)
        
        self.flickrusername_columns(treeView)
        self.show_all()
    
    def flickrusername_list_model(self, users):
        store = gtk.ListStore( str, str, str, str, gtk.gdk.Pixbuf)
        if users:
            for user in users:
                try:
                    file = '%sprofile_pic_%s' % (self.profilepics_dir, user['id'])
                    profile_pic = gtk.gdk.pixbuf_new_from_file(file)
                except Exception:
                    file = os.path.join(self.CONF_DIR, 'default.jpg')
                    profile_pic = gtk.gdk.pixbuf_new_from_file(file)
                store.append([str(user['id']), str(user['username']), str(user['realname']), str(user['location']), profile_pic])
        return store
    
    def flickrusername_columns(self, treeView):
        
        rendererText1 = gtk.CellRendererText()
        col0 = gtk.TreeViewColumn("Username")
        col0.pack_start(rendererText1, True)
        col0.set_attributes(rendererText1, text=1)
        col0.set_sort_column_id(1)
        treeView.append_column(col0)
        
        rendererText2 = gtk.CellRendererText()
        col1 = gtk.TreeViewColumn("Full Name")
        col1.pack_start(rendererText2, True)
        col1.set_attributes(rendererText2, text=2)
        col1.set_sort_column_id(2)
        treeView.append_column(col1)
        
        rendererText3 = gtk.CellRendererText()
        col2 = gtk.TreeViewColumn("Location")
        col2.pack_start(rendererText3, True)
        col2.set_attributes(rendererText3, text=3)
        col2.set_sort_column_id(3)
        treeView.append_column(col2)
        
        rendererImage = gtk.CellRendererPixbuf()
        col3 = gtk.TreeViewColumn("Photo")
        col3.pack_start(rendererImage, True)
        col3.set_attributes(rendererImage, pixbuf=4)
        treeView.append_column(col3)
        
    def flickr_set_target(self, widget, row, col):
        
        model = widget.get_model()  
        self.flickr_target.set_text(model[row][0])
        
        
        
    def update_location_list(self,  locations):
        for child in self.loc_list.get_children():
            self.loc_list.remove(child)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        self.loc_list.pack_start(sw, True, True, 0)
        store = self.location_list_model(locations)
        
        treeView = gtk.TreeView(store)
        treeView.connect("row-activated", self.location_activated)
        treeView.set_rules_hint(True)
        sw.add(treeView)
        
        self.location_columns(treeView)
        self.show_all()
    
    def location_list_model(self, locations):
        store = gtk.ListStore(str, str, str, str)
        if locations:
            for loc in locations:
                store.append([loc['context'], loc['latitude'], loc['longitude'], loc['time']])
            
        return store
    
    def location_columns(self, treeView):
       
        rendererText = gtk.CellRendererText()
        col = gtk.TreeViewColumn("Latitude", rendererText, text=1)
        treeView.append_column(col)
        
        rendererText = gtk.CellRendererText()
        col = gtk.TreeViewColumn("Longitude", rendererText, text=2)
        treeView.append_column(col)
        
        rendererText = gtk.CellRendererText()
        col = gtk.TreeViewColumn("Time", rendererText, text=3)
        col.set_sort_column_id(3)
        treeView.append_column(col)
    
    def location_activated(self, widget, row, col):
        
        model = widget.get_model()
        self.osm.set_center_and_zoom(float(model[row][1]), float(model[row][2]), 12)
        self.osm.set_zoom(self.osm.props.zoom + 3)
        self.textbuffer.set_text(model[row][0])
    
    def draw_locations(self, locations):
        pb = gtk.gdk.pixbuf_new_from_file_at_size (os.path.join(self.CONF_DIR, 'index.png'), 24,24)
        if locations:
            for l in locations:
                self.osm.image_add(float(l['latitude']), float(l['longitude']), pb)
            self.osm.set_center_and_zoom(float(locations[0]['latitude']), float(locations[0]['longitude']), 12)


    def print_tiles(self):
        if self.osm.props.tiles_queued != 0:
            return True


    def search_for_locations(self, twit, flickr):
        locations, params = self.creepy.get_locations(self.twitter_target.get_text(), self.flickr_target.get_text())
        #gobject.idle_add(self.textbuffer.set_text, 'DONE !')
        if params:
            text = ''
            for err in params['errors']:
                if err['from'] == 'twitter_connection':
                    self.create_dialog('Twitter error', 'There some failwhale issues. We were not able to retrieve all \
                    of the users tweets. \n ')
                text += 'Error while accessing %s .The problem was : %s \n ' % (err['url'], err['error'])
                
            text += ' \n %s tweets have been retrieved out of a total of %s. \n From them, we were able to extract %s locations. \n \
            We encountered %s errors in total accessing various services. \n '                                     % (params['tweets'], 
                                                                                                                      params['tweets_count'], 
                                                                                                                      params['locations'], 
                                                                                                                      len(params['errors']))
            gobject.idle_add(self.textbuffer.insert, self.textbuffer.get_end_iter(), text)       
        gobject.idle_add(self.update_location_list, locations)
        gobject.idle_add(self.draw_locations, locations)
        gobject.idle_add(self.activate_search_button)
        
    def thread_show_clicked(self, button):
        if not self.twitter_target.get_text() and not self.flickr_target.get_text():
            self.create_dialog('error', 'No targets selected. Please select at least one in targets tab')
        else:
            self.textbuffer.set_text('Searching for locations .. Be patient, I am doing my best. \n This can take a while, please hold ... \n')
            Thread(target=lambda : self.search_for_locations(self.twitter_target.get_text(),  self.flickr_target.get_text())).start()
            self.show_button.set_sensitive(0)
    def activate_search_button(self):
        self.show_button.set_sensitive(1)
    
    def create_directory(self, dir):
        try:
            os.makedirs(dir)
        except Exception, err:
            text = 'Could not create the directories for temporary data. Please check your settings. \
            Error was ' % err
            self.create_dialog('Error', text)
        
    def map_clicked(self, osm, event):
        lat,lon = self.osm.get_event_location(event).get_degrees()
        if event.button == 1:
            pass
        elif event.button == 2:
            pass
        elif event.button == 3:
            pass
    
    def create_dialog (self, title, text):
        dialog = gtk.MessageDialog(
                                   parent         = None,
                                   flags          = gtk.DIALOG_DESTROY_WITH_PARENT,
                                   type           = gtk.MESSAGE_INFO,
                                   buttons        = gtk.BUTTONS_OK,
                                   message_format = text)
        dialog.set_title(title)
        dialog.connect('response', lambda dialog, response: dialog.destroy())
        dialog.show()
    def main(self):
	self.show_all()
        if os.name == "nt": gtk.gdk.threads_enter()
        gtk.main()
        if os.name == "nt": gtk.gdk.threads_leave()

if __name__ == '__main__':
    u = CreepyUI()
    u.main()

