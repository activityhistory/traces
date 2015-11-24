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
import ast

import config as cfg

from models import Scroll, Arrangement


def parse_scrolls(session):
    # get name of file to read
    scrollfile = os.path.join(os.path.expanduser(cfg.CURRENT_DIR), cfg.SCROLLLOG)

    # read the file, write lines to database, and save lines that were not
    # written to the database
    # TODO may need to check if file is already open using a file lock
    if os.path.isfile(scrollfile):
        f = open(scrollfile, 'r+')
        lines_to_save = []
        for line in f:
            try:
                text = ast.literal_eval(line.rstrip())

                time = text['time']
                window_number = text['window_number']
                a = session.query(Arrangement).filter(Arrangement.time <= time).order_by(Arrangement.time.desc()).first()
                app_id = 0
                window_id = 0
                if a:
                    d = ast.literal_eval(a.arr)
                    for app in d:
                        # print window_number
                        # print d[app]['windows'].keys()
                        if window_number in d[app]['windows'].keys():
                            app_id = d[app]['pid']
                            window_id = d[app]['windows'][window_number]['wid']
                            break
                scroll = Scroll(text['time'], text['distance'][0], text['distance'][1], app_id, window_id)
                session.add(scroll)
            except:
                raise
                print "Could not save " + str(text) + " to the database. Saving for the next round of parsing."
                lines_to_save.append(text)
        # write lines that did not make it into the database to the start of the
        # file and delete the rest of the file
        f.seek(0)
        for line in lines_to_save:
            f.write(line)
        f.truncate()
        f.close()
