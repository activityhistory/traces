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
		last_time = 0.0
		last_x = 0.0
		last_y = 0.0
		last_window = 0
		for line in f:
			try:
				# get data from the logfile
				text = ast.literal_eval(line.rstrip())
				time = text['time']
				x = text['distance'][0]
				y = text['distance'][1]
				window_number = text['window_number']

				# ignore any rows that show no scroll distance
				if x == 0 and y == 0:
					continue

				# for first scroll just store the data locally and move to next line
				elif last_time == 0.0:
					last_time = time
					last_x = x
					last_y = y
					last_window = window_number

				# only save to database when scroll is on new window or 0.10 seconds have passed
				elif window_number == last_window and time - last_time <= 0.10:
					last_x += x
					last_y += y

				# otherwise save our stored data to the database
				else:
					a = session.query(Arrangement).filter(Arrangement.time <= time).order_by(Arrangement.time.desc()).first()
					app_id = 0
					window_id = 0
					if a:
						d = ast.literal_eval(a.arr)
						for app in d:
							if last_window in d[app]['windows'].keys():
								app_id = d[app]['pid']
								window_id = d[app]['windows'][last_window]['wid']
								break
					scroll = Scroll(last_time, last_x, last_y, app_id, window_id)
					session.add(scroll)

					# and stash the current data to be shared later
					last_time = time
					last_x = x
					last_y = y
					last_window = window_number

			except:
				print "Could not save " + str(line) + " to the database. Saving for the next round of parsing."
				lines_to_save.append(line)

		# do one more save to capture items from the last line of the log file
		try:
			scroll = Scroll(last_time, last_x, last_y, app_id, window_id)
			session.add(scroll)
		except:
			pass
		# write lines that did not make it into the database to the start of the
		# file and delete the rest of the file
		f.seek(0)
		for line in lines_to_save:
			f.write(line)
		f.truncate()
		f.close()
