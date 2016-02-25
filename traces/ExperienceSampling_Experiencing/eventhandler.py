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
from AppKit import *
from Foundation import *
from answercontroller import AnswerController

from Cocoa import (NSEvent, NSKeyDown, NSKeyDownMask, NSKeyUp, NSKeyUpMask,
				   NSFlagsChanged, NSFlagsChangedMask, NSAlternateKeyMask,
				   NSCommandKeyMask, NSControlKeyMask, NSShiftKeyMask,
				   NSAlphaShiftKeyMask)

import threading
import os
import sys
sys.path.insert(0, '..')
import functions

# from Quartz import (CFRunLoopRun, kCGWindowListOptionAll,
#					CGWindowListCopyWindowInfo, kCGNullWindowID,
#					kCGWindowListExcludeDesktopElements)

SKIP_MODIFIERS = {"", "Shift_L", "Control_L", "Super_L", "Alt_L", "Super_R",
					"Control_R", "Shift_R", "[65027]"}	# [65027] is AltGr in X

# Cocoa does not provide a good api to get the keycodes,
# therefore we have to provide our own.
KEYCODES = {
	u"\u0009": "Tab",
	u"\u001b": "Escape",
	u"\uf700": "Up",
	u"\uF701": "Down",
	u"\uF702": "Left",
	u"\uF703": "Right",
	u"\uF704": "F1",
	u"\uF705": "F2",
	u"\uF706": "F3",
	u"\uF707": "F4",
	u"\uF708": "F5",
	u"\uF709": "F6",
	u"\uF70A": "F7",
	u"\uF70B": "F8",
	u"\uF70C": "F9",
	u"\uF70D": "F10",
	u"\uF70E": "F11",
	u"\uF70F": "F12",
	u"\uF710": "F13",
	u"\uF711": "F14",
	u"\uF712": "F15",
	u"\uF713": "F16",
	u"\uF714": "F17",
	u"\uF715": "F18",
	u"\uF716": "F19",
	u"\uF717": "F20",
	u"\uF718": "F21",
	u"\uF719": "F22",
	u"\uF71A": "F23",
	u"\uF71B": "F24",
	u"\uF71C": "F25",
	u"\uF71D": "F26",
	u"\uF71E": "F27",
	u"\uF71F": "F28",
	u"\uF720": "F29",
	u"\uF721": "F30",
	u"\uF722": "F31",
	u"\uF723": "F32",
	u"\uF724": "F33",
	u"\uF725": "F34",
	u"\uF726": "F35",
	u"\uF727": "Insert",
	u"\uF728": "Delete",
	u"\uF729": "Home",
	u"\uF72A": "Begin",
	u"\uF72B": "End",
	u"\uF72C": "PageUp",
	u"\uF72D": "PageDown",
	u"\uF72E": "PrintScreen",
	u"\uF72F": "ScrollLock",
	u"\uF730": "Pause",
	u"\uF731": "SysReq",
	u"\uF732": "Break",
	u"\uF733": "Reset",
	u"\uF734": "Stop",
	u"\uF735": "Menu",
	u"\uF736": "User",
	u"\uF737": "System",
	u"\uF738": "Print",
	u"\uF739": "ClearLine",
	u"\uF73A": "ClearDisplay",
	u"\uF73B": "InsertLine",
	u"\uF73C": "DeleteLine",
	u"\uF73D": "InsertChar",
	u"\uF73E": "DeleteChar",
	u"\uF73F": "Prev",
	u"\uF740": "Next",
	u"\uF741": "Select",
	u"\uF742": "Execute",
	u"\uF743": "Undo",
	u"\uF744": "Redo",
	u"\uF745": "Find",
	u"\uF746": "Help",
	u"\uF747": "ModeSwitch"}


class EventHandler:

	def __init__(self, exp):
		self.experiment = exp
		self.simpleAnswer = AnswerController.alloc()
		self.MCQAnswer = AnswerController.alloc()
		self.answersWindow = AnswerController.alloc()
		self.randomRules = functions.getRulesByEvent(self.experiment, 1)
		self.appRules = functions.getRulesByEvent(self.experiment, 2)
		self.keyboardRules = functions.getRulesByEvent(self.experiment, 3)
		
		self.randomThread = None
		self.appThread = None
		self.keyThread = None
		
		self.workspace = None

		self.answers = []

	def start_random_handler(self):
		#if no question is already shown
		if self.simpleAnswer.shown == False and self.MCQAnswer.shown == False: 
			idToDelete = -1
			for i in range(len(self.randomRules)):
				#we make it wait the mentionned time
				if self.randomRules[i].wait == True:
					time = float(self.randomRules[i].timeToWait.split(":")[0]) * 60.0 + float(self.randomRules[i].timeToWait.split(":")[1])
					self.randomRules[i].wait = False
					self.randomThread = threading.Timer(time, self.start_random_handler)
					self.randomThread.start()
				else:
					idToDelete = i
					self.showQuestion(self.randomRules[i].question)
					break

			# if the question is shown we delete it from the rules
			if idToDelete != -1:
				del self.randomRules[idToDelete]
		else:
			if len(self.randomRules) > 0:
				self.randomThread = threading.Timer(1.0, self.start_random_handler)
				self.randomThread.start()


	def start_key_handler(self):
		#may only need the keydown mask, rather than all three
		mask = (NSKeyDownMask | NSKeyUpMask | NSFlagsChangedMask)
		NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(mask, self.key_handler)

	def start_app_handler(self):
		if self.simpleAnswer.shown == False and self.MCQAnswer.shown == False:
			if len(self.appRules) > 0:
				idToDelete = -1
				self.workspace = NSWorkspace.sharedWorkspace()
				activeApps = self.workspace.runningApplications()
				regularApps = []
				for app in activeApps:
					if app.activationPolicy() == 0: # those that show up in the Dock
						regularApps.append(app)

				# listen for window events of these applications
				for app in regularApps:
					try:
						p = int(app.processIdentifier())
						name = unicode(app.localizedName())
						for i in range(len(self.appRules)):
							if self.appRules[i].event.detail.split(": ")[1] == str(name):
								if self.appRules[i].wait == True :
									time = float(self.appRules[i].timeToWait.split(":")[0]) * 60.0 + float(self.appRules[i].timeToWait.split(":")[1])
									thread = threading.Timer(time, self.showQuestion, [self.appRules[i].question])
									thread.start()
								else:
									idToDelete = i
									self.showQuestion(self.appRules[i].question)
									break
						if idToDelete != -1:
							del self.appRules[idToDelete]
					except:
						raise
						print "Could not create event listener for application: " + str(name)
		else:
			if len(self.appRules) > 0:
				self.appThread = threading.Timer(1.0, self.start_app_handler)
				self.appThread.start()

	def key_handler(self, event):
		if self.simpleAnswer.shown == False and self.MCQAnswer.shown == False:
			if len(self.keyboardRules) > 0 :
				idToDelete = -1
				if event.type() == NSKeyDown:

					flags = event.modifierFlags()
					character = event.charactersIgnoringModifiers()
					string = KEYCODES.get(character, character)
					for i in range(len(self.keyboardRules)):

						if string == self.keyboardRules[i].event.detail[-2].lower() and (flags & NSCommandKeyMask):

							if int(self.keyboardRules[i].event.randomShortcut[0]) == int(self.keyboardRules[i].event.randomShortcut[1]):

								if self.keyboardRules[i].wait == True :

									time = float(self.keyboardRules[i].timeToWait.split(":")[0]) * 60.0 + float(self.keyboardRules[i].timeToWait.split(":")[1])
									self.keyThread = threading.Timer(time, self.showQuestion, [self.keyboardRules[i].question])
									self.keyThread.start()

								else :
									idToDelete = i
									self.showQuestion(self.keyboardRules[i].question)
									break

							else:
								self.keyboardRules[i].event.randomShortcut[0]+= 1

					if idToDelete != -1:
						del self.keyboardRules[idToDelete]
		else:
			if len(self.keyboardRules) > 0:
				self.keyThread = threading.Timer(1.0, self.key_handler, [event])
				self.keyThread.start()

	def showQuestion(self, question, modified = -1):
		if question.type == 1:
			self.simpleAnswer.initWithWindowNibName_('SimpleAnswer')
			self.simpleAnswer.showWindow_(self.simpleAnswer)
			self.answersWindow.setHandler(self)
			if modified == -1:
				self.simpleAnswer.showSimpleQuestion(question, self)
			else:
				self.simpleAnswer.showSimpleQuestion(question, self, modified)

		elif question.type == 2:
			self.MCQAnswer.initWithWindowNibName_('MCQAnswer')
			self.MCQAnswer.showWindow_(self.MCQAnswer)
			self.answersWindow.setHandler(self)
			if modified == -1:
				self.MCQAnswer.showMCQuestion(question, self)
			else:
				self.MCQAnswer.showMCQuestion(question, self, modified)

	def showAnswers(self):
		self.answersWindow.initWithWindowNibName_('Answers')
		self.answersWindow.showWindow_(self.answersWindow)
		self.answersWindow.setHandler(self)
		self.answersWindow.showAnswers(self)

	def modifyAnswer(self, id):
		for i in range(len(self.experiment.questions)):
			if self.experiment.questions[i].ununciated == self.answers[id].question:
				self.showQuestion(self.experiment.questions[i], id)

	def deleteAnswer(self, id):
		del self.answers[id]