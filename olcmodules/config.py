#!/usr/bin/env python
##############################################################################
#    OpenLFConnect
#
#    Copyright (c) 2012 Jason Pruitt <jrspruitt@gmail.com>
#
#    This file is part of OpenLFConnect.
#    OpenLFConnect is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    OpenLFConnect is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with OpenLFConnect.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################



##############################################################################
# Title:   OpenLFConnect
# Author:  Jason Pruitt
# Email:   jrspruitt@gmail.com
# IRC:     #didj irc.freenode.org
# Wiki:    http://elinux.org/LeapFrog_Pollux_Platform:_OpenLFConnect
##############################################################################

#@
# config.py Version 0.4

import os
from shutil import copytree
from olcmodules.devices import profile

APP_PATH = os.path.dirname(os.path.dirname(__file__))
FILES_PATH = os.path.join(APP_PATH, 'files')
EXTRAS_PATH = os.path.join(APP_PATH, FILES_PATH, 'Extras')
SCRIPTS_PATH = os.path.join(EXTRAS_PATH, 'Scripts')
PROFILES_PATH = os.path.join(EXTRAS_PATH, 'Profiles')
DOWNLOAD_PATH = os.path.join(FILES_PATH, 'Downloads')
INTERNAL_SCRIPTS_PATH = os.path.join(APP_PATH, 'extras/dftp_scripts')
INTERNAL_PROFILES_PATH = os.path.join(APP_PATH, 'extras/device_profiles')
HISTORY_FILE_PATH = os.path.join(FILES_PATH, '.olfc.hist')

def error(e):
    assert False, '%s' % e

        
def olc_files_dirs_check():
    try:

        if not os.path.exists(FILES_PATH):
            os.mkdir(FILES_PATH)
            print('Files folder is missing, lets repopulate.')
            print('Created %s/' % FILES_PATH)

        if not os.path.exists(HISTORY_FILE_PATH):
            open(HISTORY_FILE_PATH, 'a').close()

        dirs = [DOWNLOAD_PATH, EXTRAS_PATH, SCRIPTS_PATH, PROFILES_PATH]
                

        dprofile = profile()
        for cfg in os.listdir(INTERNAL_PROFILES_PATH):
            if cfg.endswith('.cfg') and not os.path.isdir(cfg) and cfg != 'default.cfg':
                try:
                    device_profile = dprofile.load(os.path.join(INTERNAL_PROFILES_PATH, cfg))
                    if device_profile['olfc']['create_dir'].lower() == 'true':
                        dirs.append(os.path.join(FILES_PATH, device_profile['names']['internal']))
                except Exception as e:
                    continue


        for item in dirs:
            if not os.path.exists(item):
                if item == SCRIPTS_PATH:
                    copytree(INTERNAL_SCRIPTS_PATH, SCRIPTS_PATH)
                elif item == PROFILES_PATH:
                    copytree(INTERNAL_PROFILES_PATH, PROFILES_PATH)
                else:
                    os.mkdir(item)
                
                print('Created %s/%s/' % (os.path.basename(os.path.dirname(item)), os.path.basename(item)))
            elif not os.path.isdir(item):
                error('Name conflict in files directory.')
    except Exception as e:
        error(e)




class debug(object):
    def __init__(self, module):
        self.module = module


    def wrapper(self, debug):
        if self.module.debug:
            print('-----------------')
            print(debug)
            print('\n')
            return True
        else:
            return False
    
    
    
    def make(self, path):
        debug = 'Made: %s' % os.path.basename(path)
        return self.wrapper(debug)
    
    
    
    def upload(self, lpath, rpath):
        debug = """
    local: %s
    remote: %s
            """ % (lpath, rpath)
        return self.wrapper(debug)
    
    
    
    def download(self, lpath, rpath):
        debug = """
    local: %s
    remote: %s
            """ % (lpath, rpath)
        return self.wrapper(debug)
    
    
    
    def remove(self, path):
        debug = 'Deleted: %s' % os.path.basename(path)
        return self.wrapper(debug)
    
    

    def run_script(self, path):
        debug = 'Ran Script: %s' % os.path.basename(path)
        return self.wrapper(debug)
