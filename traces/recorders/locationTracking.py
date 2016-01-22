# -*- coding: utf-8 -*-
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

This file is a translation and heavy modification from Objective-C.
The original copy-right:

//	Copyright 2009 Matt Gallagher. All rights reserved.
//
//	Permission is given to use this source code file, free of charge, in any
//	project, commercial or otherwise, entirely at your risk, with the condition
//	that any redistribution (in part or whole) of source code must retain
//	this copyright and permission notice. Attribution in compiled projects is
//	appreciated but not required.
"""

import objc
import CoreLocation
from CoreLocation import *
import math

class LocationTracking:
	locationManager = objc.ivar()

	def __init__(self):
		self.locationchange_hook = lambda x: True

	def startTracking(self):
		print "start tracking location "
		self.locationManager = CoreLocation.CLLocationManager.alloc().init()
		self.locationManager.startUpdatingLocation()
		# self.locationManager.startMonitoringSignificantLocationChanges()
		print "location ", self.locationManager._.location
		# print self.locationManager._.location.description()

	@classmethod
	def latitudeRangeForLocation_(self, aLocation):
		M = 6367000.0 # approximate average meridional radius of curvature of earth
		metersToLatitude = 1.0 / ((math.pi / 180.0) * M)
		accuracyToWindowScale = 2.0

		return aLocation.horizontalAccuracy() * metersToLatitude * accuracyToWindowScale

	@classmethod
	def longitudeRangeForLocation_(self, aLocation):
		latitudeRange = LocationTracking.latitudeRangeForLocation_(aLocation)

		return latitudeRange * math.cos(aLocation.coordinate().latitude * math.pi / 180.0)

	def locationManager_didUpdateToLocation_fromLocation_(self,
			manager, newLocation, oldLocation):

		print "location update"

		# Ignore updates where nothing we care about changed
		if newLocation is None:
			return
		if oldLocation is None:
			pass
		elif (newLocation.coordinate().longitude == oldLocation.coordinate().longitude and
				newLocation.coordinate().latitude == oldLocation.coordinate().latitude and
				newLocation.horizontalAccuracy() == oldLocation.horizontalAccuracy()):
			return

		print "location ", newLocation.coordinate().latitude, newLocation.coordinate().longitude, LocationTracking.latitudeRangeForLocation_(newLocation), LocationTracking.longitudeRangeForLocation_(newLocation)

		self.locationchange_hook(newLocation.coordinate().latitude,
			newLocation.coordinate().longitude,
			LocationTracking.latitudeRangeForLocation_(newLocation),
			LocationTracking.longitudeRangeForLocation_(newLocation))

		# TODO what happens in case of new location.
		# newLocation.coordinate().latitude,
		# newLocation.coordinate().longitude,
		# LocationTracking.latitudeRangeForLocation_(newLocation),
		# LocationTracking.longitudeRangeForLocation_(newLocation))

	def locationManager_didFailWithError_(self, manager, error):
		print "location error"
		print error.localizedDescription()

	def stopTracking(self, aNotification):
		self.locationManager.stopUpdatingLocation()
