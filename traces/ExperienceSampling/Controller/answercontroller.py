# -*- coding: utf-8 -*-

from Cocoa import *
from Foundation import NSObject

import sys
sys.path.insert(0, '..')
from Model.Experiment import Experiment
import functions

class AnswerController(NSWindowController):

	ununciated = objc.IBOutlet()
	textAnswer = objc.IBOutlet()
	choiceAnswer = objc.IBOutlet()

	choice1 = objc.IBOutlet()
	choice2 = objc.IBOutlet()
	choice3 = objc.IBOutlet()
	choice4 = objc.IBOutlet()
	
	answerWindow = objc.IBOutlet()

	def windowDidLoad(self):
		NSWindowController.windowDidLoad(self)
		self.experiment = Experiment()

	def orderOut(self):
		self.answerWindow.orderOut_(self.window)

	def showSimpleQuestion(self, question):
		self.ununciated.setStringValue_(question.ununciated)
		self.ununciated.setHidden_(False)
		self.answerWindow.makeKeyAndOrderFront_(self.answerWindow)

	def showMCQuestion(self, question):
		self.ununciated.setStringValue_(question.ununciated)
		self.ununciated.setHidden_(False)

		for i in range(len(question.choices)):
			exec("self.choice%d.setTitle_('%s')" % (i+1, question.choices[i]))
			exec("self.choice%d.setTransparent_(False)" % (i+1))

		self.answerWindow.makeKeyAndOrderFront_(self.answerWindow)

	def setExperiment(self, exp):
		self.experiment = exp

	@objc.IBAction
	def submitSimpleAnswer_(self, sender):
		self.answerWindow.close()

	@objc.IBAction
	def submitMCQAnswer_(self, sender):
		self.answerWindow.orderOut_(self.answerWindow)