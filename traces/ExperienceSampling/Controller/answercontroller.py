# -*- coding: utf-8 -*-

from Cocoa import *
from Foundation import NSObject

class AnswerController(NSWindowController):

	ununciated = objc.IBOutlet()
	answer = objc.IBOutlet()
	window = objc.IBOutlet()

	def windowDidLoad(self):
		
		NSWindowController.windowDidLoad(self)
		self.experiment = None
		self.ununciated.setStringValue_(self.experiment.questions[0].ununciated)
		self.ununciated.setHidden_(False)


	def setExperiment(self, exp):
		self.experiment = exp

	@objc.IBAction
	def submitAnswer_(self, sender):
		self.test = self.answer.stringValue()
		print self.test
		self.window.orderOut_(self.window)
