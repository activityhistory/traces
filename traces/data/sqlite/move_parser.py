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

from models import Move


def parse_moves(session):
    # get name of file
    movefile = os.path.join(os.path.expanduser(cfg.CURRENT_DIR), cfg.MOVELOG)

    # read the file, write lines to database, and save lines that were not
    # written to the database
    # TODO may need to check if file is already open using a file lock
    if os.path.isfile(movefile):
        f = open(movefile, 'r+')
        lines_to_save = []
        last_location = (0,0)
        last_time = 0.0

        for line in f:
            try:
                text = ast.literal_eval(line.rstrip())
                time = text['time']
                location = text['location']
                # throttle mouse tracking to 10Hz
                if location == last_location or time-last_time < 0.1:
                    continue
                move = Move(time, location[0], location[1])
                session.add(move)
                last_location = location
                last_time = time
            except:
                print "Could not save " + str(text) + " to the database. Saving for the next round of parsing."
                lines_to_save.append(text)
        # write lines that did not make it into the database to the start of the
        # file and delete the rest of the file
        f.seek(0)
        for line in lines_to_save:
            f.write(line)
        f.truncate()
        f.close()
