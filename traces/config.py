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

import time

# where to look for detachable volumes, like USB keys
VOLUMES = '/Volumes'

# log files
RECORDERLOG = 'recorder.log'
APPLOG = 'app.log'
CLICKLOG = 'click.log'
CLIPLOG = 'clip.log'
GEOLOG = 'geometry.log'
KEYLOG = 'key.log'
MOVELOG = 'move.log'
SCROLLLOG = 'scroll.log'
WINDOWLOG = 'window.log'
TABLOG = 'tab.log'

# set storage to "mongo" to use mongodb
# set storage to "sqlite" to use sqlite
STORAGE = "sqlite"

# mongodb names
DB = "traces"
SQLDB = "traces.sqlite"
RECORDERCOL = "recorder"
APPCOL = "apps"
CLICKCOL = "clicks"
GEOCOL = "geometry"
KEYCOL = "keys"
MOVECOL = "moves"
SCROLLCOL = "scrolls"
WINDOWCOL = 'windows'
TABCOL = 'tabs'

# data directories
LOCAL_DIR = '~/.traces'
THUMBDRIVE_DIR = None
CURRENT_DIR = None
# DBNAME = 'selfspy.sqlite'

# times
NOW = time.time
PARSEDELAY = 15
CLIPDELAY = 1
