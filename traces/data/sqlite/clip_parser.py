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

from models import Clipboard


def parse_clips(session):
	# get names of files to read and mongodb collection to write
	clipfile = os.path.join(os.path.expanduser(cfg.CURRENT_DIR), cfg.CLIPLOG)

	# read the file, write lines to database, and save lines that were not
	# written to the database
	if os.path.isfile(clipfile):
		f = open(clipfile, 'r+')
		lines_to_save = []
		for line in f:
			try:
				text = ast.literal_eval(line.rstrip())
				clip = Clipboard(text['time'], text['text'], text['url'], text['image'])
				session.add(clip)
			except:
				print "Could not save " + str(line) + " to the database. Saving for the next round of parsing."
				lines_to_save.append(line)
		# write lines that did not make it into the database to the start of the
		# file and delete the rest of the file
		f.seek(0)
		for line in lines_to_save:
			f.write(line)
		f.truncate()
		f.close()
