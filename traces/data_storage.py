# -*- coding: utf-8 -*-
"""
Traces: Activity Tracker
Copyright (C) 2015 Adam Rule
with Aurélien Tabard, Jonas Keper, Azeem Ghumman, and Maxime Guyaux

Inspired by Selfspy and Burrito
https://github.com/gurgeh/selfspy
https://github.com/pgbovine/burrito/

You should have received a copy of the GNU General Public License
along with Traces. If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import config as cfg

def createDataDirectories(d):
    """
    Create directories to store data

    d: string of full patch to data storage directory
    """

    # main directory
    try:
        os.makedirs(d)
    except OSError:
        pass

    # screenshot directory
    try:
        os.makedirs(os.path.join(d, 'screenshots'))
    except OSError:
        pass

    # audio directory
    try:
        os.makedirs(os.path.join(d, 'audio'))
    except OSError:
        pass

def checkDrive():
    lookupThumbdrive()
    defineCurrentDrive()

def lookupThumbdrive(namefilter=""):
    for directory in os.listdir(cfg.VOLUMES) :
        if namefilter in directory :
            volume = os.path.join(cfg.VOLUMES, directory)
            if (os.path.ismount(volume)) :
                subDirs = os.listdir(volume)
                for filename in subDirs:
                    if "traces.cfg" == filename :
                        print "backup drive found ", volume
                        cfg.THUMBDRIVE_DIR = volume
                        return cfg.THUMBDRIVE_DIR
    return None

def defineCurrentDrive():
    if (isThumbdrivePlugged()):
        cfg.CURRENT_DIR = cfg.THUMBDRIVE_DIR
    else:
        cfg.CURRENT_DIR = os.path.expanduser(cfg.LOCAL_DIR)

def isThumbdrivePlugged():
    if (cfg.THUMBDRIVE_DIR != None and cfg.THUMBDRIVE_DIR != ""):
        if (os.path.ismount(cfg.THUMBDRIVE_DIR)):
            return True
        else :
            # TODO display alert message
            print "Thumbdrive defined but not plugged in"
            cfg.THUMBDRIVE_DIR = None
            lookupThumbdrive()
            return False
    else :
        return False
