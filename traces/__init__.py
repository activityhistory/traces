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

import data_storage
import config as cfg
from activity_tracker import ActivityTracker


def main():
    print "Traces is starting"

    # find if external drives at attached for recording
    data_storage.checkDrive()

    # create directories to store data,
    data_storage.createDataDirectories(os.path.expanduser(cfg.LOCAL_DIR))

    # start activity tracker
    astore = ActivityTracker()
    try:
        astore.run()
    except SystemExit:
        astore.close()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
