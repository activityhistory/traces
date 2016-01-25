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

from models import Click, AppEvent, WindowEvent


def parse_clicks(session):
	# get names of files to read and mongodb collection to write
	clickfile = os.path.join(os.path.expanduser(cfg.CURRENT_DIR), cfg.CLICKLOG)

	# read the file, write lines to database, and save lines that were not
	# written to the database
	# TODO may need to check if file is already open using a file lock
	if os.path.isfile(clickfile):
		f = open(clickfile, 'r+')
		lines_to_save = []
		for line in f:
			try:
				text = ast.literal_eval(line.rstrip())

				# get active app and window at time of event
				app = session.query(AppEvent).filter(AppEvent.event=="Active", AppEvent.time<=text['time']).order_by(AppEvent.time.desc()).first()
				window = session.query(WindowEvent).filter(WindowEvent.event=="Active", WindowEvent.time <= text['time']).order_by(WindowEvent.time.desc()).first()
				pid = app.app_id if app else 0
				wid = window.window_id if window else 0

				click = Click(text['time'], text['button'], text['location'][0], text['location'][1], pid, wid)
				session.add(click)
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
