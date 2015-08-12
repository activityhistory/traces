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
