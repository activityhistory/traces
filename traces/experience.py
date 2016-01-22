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
import re
import string
import threading

import objc
from objc import IBAction, IBOutlet

from Foundation import *
from AppKit import *

from Cocoa import NSCommandKeyMask, NSTimer

import config as cfg
from data.sqlite.models import Experience

from datetime import datetime

import mutagen.mp4


# Experience Sampling window controller
class ExperienceController(NSWindowController):

	# outlets for UI elements
	experienceText = IBOutlet()
	recordButton = IBOutlet()
	playAudioButton = IBOutlet()
	deleteAudioButton = IBOutlet()
	progressBar = IBOutlet()

	recordingAudio = False
	playingAudio = False
	audio_file = ''

	@IBAction
	def recordText_(self, sender):
		t = cfg.NOW()
		message = self.experienceText.stringValue()
		e = Experience(t, message)
		self.sniffer.activity_tracker.storage.session.add(e)
		# may not need to commit here, but could wait till next round of parsing
		self.sniffer.activity_tracker.storage.sqlcommit()

		print 'Received experience message of: ' + message
		self.expController.close()

	@IBAction
	def toggleAudioRecording_(self, sender):
		if self.recordingAudio:
			self.recordingAudio = False
			print "Stop audio message"

			# get the right name for our audio file
			dt = datetime.now().strftime("%y%m%d-%H%M%S%f")
			audioName = str(os.path.join(cfg.CURRENT_DIR, "audio/")) + dt + '.m4a'
			self.audio_file = audioName
			audioName = string.replace(audioName, "/", ":")
			audioName = audioName[1:]

			# start the audio recording
			s = NSAppleScript.alloc().initWithSource_("set filePath to \"" + audioName + "\" \n set placetosaveFile to a reference to file filePath \n tell application \"QuickTime Player\" \n set mydocument to document 1 \n tell document 1 \n stop \n end tell \n set newRecordingDoc to first document whose name = \"untitled\" \n export newRecordingDoc in placetosaveFile using settings preset \"Audio Only\" \n close newRecordingDoc without saving \n quit \n end tell")
			s.executeAndReturnError_(None)

			# log the experience in our table
			t = cfg.NOW()
			e = Experience(t, dt + '.m4a')
			self.sniffer.activity_tracker.storage.session.add(e)
			# may not need to commit here, but could wait till next round of parsing
			self.sniffer.activity_tracker.storage.sqlcommit()

			# reset controls
			self.expController.recordButton.setTitle_("Record")
			self.expController.recordButton.setEnabled_(False)
			self.expController.playAudioButton.setHidden_(False)
			self.expController.deleteAudioButton.setHidden_(False)
			self.expController.progressBar.setHidden_(False)

		else:
			self.recordingAudio = True
			print "Start audio message"

			s = NSAppleScript.alloc().initWithSource_("tell application \"QuickTime Player\" \n set new_recording to (new audio recording) \n tell new_recording \n start \n end tell \n tell application \"System Events\" \n set visible of process \"QuickTime Player\" to false \n repeat until visible of process \"QuickTime Player\" is false \n end repeat \n end tell \n end tell")
			s.executeAndReturnError_(None)

			self.expController.recordButton.setTitle_("Stop Recording")
			# TODO change button color to red while recording

	@IBAction
	def toggleAudioPlay_(self, sender):
		if self.playingAudio:
			self.stopAudioPlay()

		else:
			self.playingAudio = True
			self.expController.playAudioButton.setTitle_("Stop")

			s = NSAppleScript.alloc().initWithSource_("set filePath to POSIX file \"" + self.audio_file + "\" \n tell application \"QuickTime Player\" \n open filePath \n tell application \"System Events\" \n set visible of process \"QuickTime Player\" to false \n repeat until visible of process \"QuickTime Player\" is false \n end repeat \n end tell \n play the front document \n end tell")
			s.executeAndReturnError_(None)

			# Stop playback once end of audio file is reached
			length = mutagen.mp4.MP4(self.audio_file).info.length
			stop_thread = threading.Timer(length, self.stopAudioPlay)
			stop_thread.start()

			if length >= 1.0:
				advance_thread = threading.Timer(1.0, self.incrementProgressBar, [1.0, length])
				advance_thread.start()

			# s = objc.selector(self.stopAudioPlay,signature='v@:')
			# self.playbackTimer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(length, self, s, None, False)

	def incrementProgressBar(self, t, m):
		print "Got to incrementor"
		i = 1.0/m * 100.0
		self.expController.progressBar.incrementBy_(i)
		if t < m - 1.0:
			t += 1.0
			advance_thread = threading.Timer(1.0, self.incrementProgressBar, [t, m])
			advance_thread.start()

	def stopAudioPlay(self):
		self.playingAudio = False
		self.expController.playAudioButton.setTitle_("Play")
		value = self.expController.progressBar.doubleValue()
		self.expController.progressBar.incrementBy_(100.0 - value)
		self.expController.progressBar.incrementBy_(-100.0)

		s = NSAppleScript.alloc().initWithSource_("tell application \"QuickTime Player\" \n stop the front document \n close the front document \n end tell")
		s.executeAndReturnError_(None)

	@IBAction
	def deleteAudio_(self, sender):
		if (self.audio_file != '') & (self.audio_file != None) :
			if os.path.exists(self.audio_file):
				os.remove(self.audio_file)
		self.audio_file = ''

		# reset button visibility
		self.expController.recordButton.setEnabled_(True)
		self.expController.playAudioButton.setHidden_(True)
		self.expController.deleteAudioButton.setHidden_(True)
		self.expController.progressBar.setHidden_(True)

	# override window close to track when users close the experience window
	def overrideClose(self):
		s = objc.selector(self.setIgnoredAndClose_,signature='v@:@')
		self.expController.window().standardWindowButton_(NSWindowCloseButton).setTarget_(self.expController)
		self.expController.window().standardWindowButton_(NSWindowCloseButton).setAction_(s)
		self.expController.window().standardWindowButton_(NSWindowCloseButton).setKeyEquivalentModifierMask_(NSCommandKeyMask)
		self.expController.window().standardWindowButton_(NSWindowCloseButton).setKeyEquivalent_("w")

	def setIgnoredAndClose_(self, notification):
		self.ignored = True
		NSNotificationCenter.defaultCenter().postNotificationName_object_('experienceReceived',self)
		self.expController.close()

	def windowDidLoad(self):
		NSWindowController.windowDidLoad(self)

	def show(self, sniffer):
		try:
			# close the window if its already open
			if self.expController.window().isVisible():
				self.expController.close()
		except:
			pass

		self.sniffer = sniffer

		# open window from NIB file, show front and center
		self.expController = ExperienceController.alloc().initWithWindowNibName_("experience")
		self.expController.showWindow_(None)
		self.expController.window().makeKeyAndOrderFront_(None)
		self.expController.window().center()
		self.expController.retain()

		# needed to show window on top of other applications
		# NSNotificationCenter.defaultCenter().postNotificationName_object_('makeAppActive',self)

		self.sniffer.app.activateIgnoringOtherApps_(True)

		self.overrideClose(self)

		return self.expController

	show = classmethod(show)
