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
import sys
import json
import data
import config as cfg
from activity_tracker import ActivityTracker

from ExperienceSampling import functions

def main():
	print "Traces is starting"

	# setting a utf8 as the default encoding
	reload(sys)
	sys.setdefaultencoding('utf8')

	# find if external drives are attached for storing recording data
	data.checkDrive()

	# create directories to store data, if needed
	data.createDataDirectories(os.path.expanduser(cfg.CURRENT_DIR))

	if os.path.isfile(os.path.expanduser("~") + "/.traces/config.log"):
		
		print "Experience Sampling is starting"
		fileJson = open(os.path.expanduser("~") + "/.traces/config.log", 'r')
		dataJson = json.load(fileJson)
		experiment = functions.loadJson(dataJson)
		functions.displayExperiment(experiment)
		
		"""exp = EventHandler(experiment)

		if len(exp.randomRules) > 0:
			print "there are some random rules"
			exp.start_random_handler()

		if len(exp.appRules) > 0:
			print "there are some app rules"
			exp.appThread = threading.Timer(5.0, exp.start_app_handler)
			exp.appThread.start()

		if len(exp.keyboardRules) > 0:
			print "there are some keyboard rules"
			exp.start_key_handler()


	# start activity tracker
	astore = ActivityTracker()
	try:
		astore.run()
	except SystemExit:
		astore.close()
	except KeyboardInterrupt:
		pass
	"""

if __name__ == '__main__':
	main()
