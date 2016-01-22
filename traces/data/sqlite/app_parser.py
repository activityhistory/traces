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
import copy
import ast

import config as cfg
import utils_cocoa

from models import (App, AppEvent, Window, WindowEvent, Geometry, Arrangement, URL, URLEvent)


def parse_apps(session, activity_tracker):
	#TODO see if there is a way to query the database only for a list of app names
	# get a copy of the starting database so we don't have to query it all the time
	apps = session.query(App).all()
	app_names = []
	for a in apps:
		app_names.append(a.name)

	# read the file, write new apps and events to the database
	appfile = os.path.join(os.path.expanduser(cfg.CURRENT_DIR), cfg.APPLOG)
	if os.path.isfile(appfile):
		f = open(appfile, 'r+')
		lines_to_save = []

		for line in f:
			try:
				# get data from the line of text
				text = ast.literal_eval(line.rstrip())
				t = text['time']
				event = text['type']
				app_name = text['app']
				pid = None

				# get pid of app from database, add app to database if not already there
				if app_name not in app_names:
					# add app to the database
					app_to_add = App(t, app_name)
					session.add(app_to_add)
					activity_tracker.storage.sqlcommit()

					# update our local app list
					apps = session.query(App).all()
					app_names = [a.name for a in apps]

				pid = app_names.index(app_name) + 1 # array starts at 0, database ids a 1

				# add the app event to the database
				ae = AppEvent(t, pid, event)
				session.add(ae)

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

def parse_windows(session, activity_tracker):
	# get a copy of the starting app database so we don't have to query it all the time
	apps = session.query(App).all()
	app_names = [a.name for a in apps]

	# get a copy of the starting window database so we don't have to query it all the time
	windows = session.query(Window).all()
	window_names = [w.title for w in windows]

	# read the file, write lines to database, and save lines that were not
	# written to the database
	windowfile = os.path.join(os.path.expanduser(cfg.CURRENT_DIR), cfg.WINDOWLOG)
	if os.path.isfile(windowfile):
		f = open(windowfile, 'r+')
		lines_to_save = []
		for line in f:
			try:
				text = ast.literal_eval(line.rstrip())
				t = text['time']
				event = text['type']
				app_name = text['app']
				window = text['window']

				# for now let's only save open, close, active, inactive
				if event not in ['Open', 'Close', 'Active', 'Inactive']:
					continue

				if app_name not in app_names:
					# add app to the database
					app_to_add = App(t, app_name)
					session.add(app_to_add)
					#TODO catch if our commit fails
					activity_tracker.storage.sqlcommit()

					# update our local app list
					apps = session.query(App).all()
					app_names = [a.name for a in apps]

				pid = app_names.index(app_name) + 1 # array starts at 0, database ids a 1

				if window not in window_names:
					# add app to the database
					app_to_add = Window(t, pid, window)
					session.add(app_to_add)
					#TODO catch if our commit fails
					activity_tracker.storage.sqlcommit()

					# update our local app list
					windows = session.query(Window).all()
					window_names = [w.title for w in windows]

				wid = window_names.index(window) + 1 # array starts at 0, database ids a 1

				# add the window event to the database
				we = WindowEvent(t, wid, event)
				session.add(we)

			except:
				raise
				print "Could not save " + str(line) + " to the database. Saving for the next round of parsing."
				lines_to_save.append(line)
		# write lines that did not make it into the database to the start of the
		# file and delete the rest of the file
		f.seek(0)
		for line in lines_to_save:
			f.write(line)
		f.truncate()
		f.close()

def parse_geometries(session, activity_tracker):
	# get names of file to read and the last arrangement
	geofile = os.path.join(os.path.expanduser(cfg.CURRENT_DIR), cfg.GEOLOG)
	q = session.query(Arrangement).order_by(Arrangement.id.desc()).first()
	last_arr = ast.literal_eval(q.arr) if q else {}

	# clean up dictionary for equal comparison
	for a, va in last_arr.iteritems():
		del va['pid']
		for w, vw in va['windows'].iteritems():
			del vw['wid']
			del vw['gid']

	# check if db file
	if os.path.isfile(geofile):
		f = open(geofile, 'r+')
		lines_to_save = []

		# get existing apps from the database
		apps = session.query(App).all()
		app_names = [a.name for a in apps]

		# get existing windows from the database
		windows = session.query(Window).all()
		window_names = [w.title for w in windows]

		# get existing geometries from the database
		geometries = session.query(Geometry).all()
		geometry_dicts = [[g.x, g.y, g.w, g.h] for g in geometries]

		# get existing urls from the database
		db_urls = session.query(URL).all()
		urls = [d.url for d in db_urls]

		for line in f:
			try:
				# get data
				text = ast.literal_eval(line.rstrip())
				t = text['time']
				arrangement = text['geometry']

				# if this is a duplicate of the last arrangement, don't record it
				if arrangement == last_arr:
					continue

				# check for new windows opened or activated
				for app, value in arrangement.iteritems():
					app_name = value['name']
					active = value['active']
					windows = value['windows']

					# add new apps to the database, but should not need to to this
					if app_name not in app_names:
						# add app to the database
						app_to_add = App(t, app_name)
						session.add(app_to_add)
						activity_tracker.storage.sqlcommit()

						# update our local app list
						apps = session.query(App).all()
						app_names = [a.name for a in apps]

					# add the app's pid to the arrangement dictionary
					pid = app_names.index(app_name) + 1 # array starts at 0, database ids a 1
					value['pid'] = pid # removing for now, may want to add back later, but will need new arrangement comparison method

					for window, val in windows.iteritems():
						# get window information
						title = val['name']
						w_active = val['active']
						bounds = val['bounds']
						x = int(bounds['x'])
						y = int(bounds['y'])
						width =	 int(bounds['width'])
						height = int(bounds['height'])

						# add new windows to the database, but should not need to do this
						if title not in window_names:
							# add app to the database
							app_to_add = Window(t, pid, title)
							session.add(app_to_add)
							activity_tracker.storage.sqlcommit()

							# update our local window list
							windows = session.query(Window).all()
							window_names = [w.title for w in windows]

						# add the window's wid to the window dictionary
						wid = window_names.index(title) + 1 # array starts at 0, database ids a 1
						val['wid'] = wid # removing for now, may want to add back later, but will need new arrangement comparison method

						# add new geometries to the database
						gd = [x, y, width, height]
						if gd not in geometry_dicts:
							ge = Geometry(t, x, y, width, height)
							session.add(ge)
							activity_tracker.storage.sqlcommit()

							# update our local geomery list
							geometries = session.query(Geometry).all()
							geometry_dicts = [[g.x, g.y, g.w, g.h] for g in geometries]

						# add the geometry's gid to the window dictionary
						gid = geometry_dicts.index(gd) + 1 # array starts at 0, database ids a 1
						val['gid'] = gid # removing for now, may want to add back later, but will need new arrangement comparison method

						# add new urls to the database
						if 'tabs' in val.keys():
							tabs = val['tabs']
							for tab, tval in tabs.iteritems():
								t_active = tval['active']
								t_url = tval['url']
								if tval['url'] not in urls:
									u = URL(t, tval['title'], tval['url'], tval['host'])
									session.add(u)
									activity_tracker.storage.sqlcommit()

									# update our local urls list
									db_urls = session.query(URL).all()
									urls = [d.url for d in db_urls]

								# add the url's uid to the window dictionary
								uid = urls.index(tval['url']) + 1 # array starts at 0, database ids a 1
								tval['uid'] = uid

								#TODO create url open, close, active, inactive events
								if not app in last_arr:
									te = URLEvent(t, uid, pid, wid, "Open")
									session.add(te)
									if t_active:
										te = URLEvent(t, uid, pid, wid, "Open")
										session.add(te)
								elif not window in last_arr[app]['windows']:
									te = URLEvent(t, uid, pid, wid, "Open")
									session.add(te)
									if t_active:
										te = URLEvent(t, uid, pid, wid, "Active")
										session.add(te)
								elif not tab in last_arr[app]['windows'][window]['tabs']:
									te = URLEvent(t, uid, pid, wid, "Open")
									session.add(te)
									if t_active:
										te = URLEvent(t, uid, pid, wid, "Active")
										session.add(te)
								elif t_active and (not last_arr[app]['windows'][window]['tabs'][tab]['active'] or t_url != last_arr[app]['windows'][window]['tabs'][tab]['url']):
									te = URLEvent(t, uid, pid, wid, "Active")
									session.add(te)

						# create open and active events if...
						# this app was not even open the last time around
						if not app in last_arr:
							we = WindowEvent(t, wid, "Open")
							session.add(we)
							if w_active:
								we = WindowEvent(t, wid, "Active")
								session.add(we)

						else:
							# or if the window was not present last time
							if not window in last_arr[app]['windows']:
								we = WindowEvent(t, wid, "Open")
								session.add(we)
								if w_active:
									we = WindowEvent(t, wid, "Active")
									session.add(we)
							else:
								# or the window was present but not active last time, or had a different name
								if w_active and (not last_arr[app]['windows'][window]['active'] or title != last_arr[app]['windows'][window]['name']):
									we = WindowEvent(t, wid, "Active")
									session.add(we)

				# add new arrangement to the database
				arr_to_add = Arrangement(t, str(arrangement))
				session.add(arr_to_add)

				# look now at the last arrangement to see what has closed or gone inactive
				for app, value in last_arr.iteritems():
					app_name = value['name']
					active = value['active']
					windows = value['windows']

					if app_name not in app_names:
						# add app to the database
						app_to_add = App(t, app_name)
						session.add(app_to_add)
						#TODO catch if our commit fails
						activity_tracker.storage.sqlcommit()

						# update our local app list
						apps = session.query(App).all()
						app_names = [a.name for a in apps]

					pid = app_names.index(app_name) + 1 # array starts at 0, database ids a 1

					for window, val in windows.iteritems():
						# get window information
						title = val['name']
						w_active = val['active']
						bounds = val['bounds']
						x = bounds['x']
						y = bounds['y']
						w =	 bounds['width']
						h = bounds['height']

						if title not in window_names:
							# add app to the database
							app_to_add = Window(t, pid, title)
							session.add(app_to_add)
							#TODO catch if our commit fails
							activity_tracker.storage.sqlcommit()

							# update our local app list
							windows = session.query(Window).all()
							window_names = [w.title for w in windows]

						wid = window_names.index(title) + 1 # array starts at 0, database ids a 1

						if 'tabs' in val.keys():
							tabs = val['tabs']
							for tab, tval in tabs.iteritems():
								uid = urls.index(tval['url']) + 1
								t_active = tval['active']
								t_url = tval['url']
								if not app in arrangement:
									te = URLEvent(t, uid, pid, wid, "Close")
									session.add(te)
									if t_active:
										te = URLEvent(t, uid, pid, wid, "Inactive")
										session.add(te)
								elif not window in arrangement[app]['windows']:
									te = URLEvent(t, uid, pid, wid, "Close")
									session.add(te)
									if t_active:
										te = URLEvent(t, uid, pid, wid, "Inactive")
										session.add(te)
								elif not tab in arrangement[app]['windows'][window]['tabs']:
									te = URLEvent(t, uid, pid, wid, "Close")
									session.add(te)
									if t_active:
										te = URLEvent(t, uid, pid, wid, "Inactive")
										session.add(te)
								elif t_active and (not arrangement[app]['windows'][window]['tabs'][tab]['active'] or t_url != arrangement[app]['windows'][window]['tabs'][tab]['url']):
									te = URLEvent(t, uid, pid, wid, "Inactive")
									session.add(te)

						# create close and inactive events if...
						# this app is not longer present
						if not app in arrangement:
							we = WindowEvent(t, wid, "Close")# create open event
							session.add(we)
							if w_active:
								we = WindowEvent(t, wid, "Inactive")# create open event
								session.add(we)

						else:
							# or if the window is not longer present
							if not window in arrangement[app]['windows']:
								we = WindowEvent(t, wid, "Close")# create open event
								session.add(we)
								if w_active:
									we = WindowEvent(t, wid, "Inactive")# create open event
									session.add(we)
							else:
								# or the window is present but no longer active, or has a different name
								if w_active and (not arrangement[app]['windows'][window]['active'] or title != arrangement[app]['windows'][window]['name']):
									we = WindowEvent(t, wid, "Inactive")# create open event
									session.add(we)

				last_arr = copy.deepcopy(arrangement)

			except:
				raise
				print "Could not save " + str(line) + " to the database. Saving for the next round of parsing."
				lines_to_save.append(line)

		# write lines that did not make it into the database to the start of the
		# file and delete the rest of the file
		f.seek(0)
		for line in lines_to_save:
			f.write(line)
		f.truncate()
		f.close()
