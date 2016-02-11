# -*- coding: utf-8 -*-

from Cocoa import *
from Foundation import NSObject

import sys
sys.path.insert(0, '..')
from Model.Experiment import Experiment
import functions

class AnswerController(NSWindowController):

	ununciated = objc.IBOutlet()
	answer = objc.IBOutlet()
	answerWindow = objc.IBOutlet()

	def windowDidLoad(self):
		NSWindowController.windowDidLoad(self)
		self.experiment = Experiment()

	def orderOut(self):
		self.answerWindow.orderOut_(self.window)

	def showQuestion(self, question):
		self.ununciated.setStringValue_(question.ununciated)
		self.ununciated.setHidden_(False)
		self.answerWindow.makeKeyAndOrderFront_(self.answerWindow)

	def setExperiment(self, exp):
		self.experiment = exp

	@objc.IBAction
	def submitAnswer_(self, sender):
		self.answerWindow.orderOut_(self.answerWindow)
