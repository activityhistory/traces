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

from Foundation import *
import config as cfg

from AppKit import *


def show_alert(message):
    """
    Shows a pop-over alert on the screen

    message: String of text to display in alert
    """

    print str(message)

    alert = NSAlert.alloc().init()
    alert.addButtonWithTitle_("OK")
    alert.setMessageText_(str(message))
    alert.setAlertStyle_(NSWarningAlertStyle)
    alert.runModal()

    sys.exit()

def write_to_file(text, fi):
    full_file = os.path.join(os.path.expanduser(cfg.CURRENT_DIR), fi)
    f = open(full_file, 'a')
    print >>f, text
    f.close()

# TODO find a way to not throw away the charachters we cannot recognize
def ascii_encode(text):
    return text.encode('ascii', 'replace')
    # return string.encode('ascii', 'backslashreplace')
    # return text.dataUsingEncoding_allowLossyConversion_(NSASCIIStringEncoding,True)

def safari_to_unix(t):
    # Apple measures time in seconds since 12:00AM Jan 1, 2001 (978307200 seconds after the epoch)
    return t + 978307200

def unix_to_safari(t):
    # Apple measures time in seconds since 12:00AM Jan 1, 2001 (978307200 seconds after the epoch)
    return t - 978307200

def chrome_to_unix(t):
    # Chrome measures time in 100 nanosecond chunks since  12:00AM Jan 1, 1601
    # there are 11,644,473,600 seconds between start of Chrome time and epoch time
    return t / 1000000 - 11644473600

def unix_to_chrome(t):
    # Chrome measures time in 100 nanosecond chunks since  12:00AM Jan 1, 1601
    # there are 11,644,473,600 seconds between start of Chrome time and epoch time
    return (t + 11644473600)*1000000
