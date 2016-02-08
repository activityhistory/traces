# -*- coding: utf-8 -*-

from Cocoa import *
from Foundation import NSObject
from questioncontroller import QuestionController
from answercontroller import AnswerController
import sys
sys.path.insert(0, '..')

from Model.Experiment import Experiment

class MainController(NSWindowController):

	nbQuestions = objc.IBOutlet()
	nbRules = objc.IBOutlet()

	def windowDidLoad(self):
		NSWindowController.windowDidLoad(self)
		self.experiment = Experiment()
		self.questionsConfig = QuestionController.alloc().initWithWindowNibName_('Question')
		self.answer = AnswerController.alloc()

	def updateDisplay(self):
		self.nbQuestions.setStringValue_(self.experiment.countQuestions())
		self.nbRules.setStringValue_(self.experiment.countRules())

	@objc.IBAction
	def addQuestion_(self, sender):
		self.questionsConfig.showWindow_(self.questionsConfig)
		self.questionsConfig.showAddWindow()
		self.questionsConfig.setExperiment(self.experiment)
		self.questionsConfig.setMainController(self)

	@objc.IBAction
	def showQuestions_(self, sender):
		self.questionsConfig.showWindow_(self.questionsConfig)
		self.questionsConfig.showQuestions()
		self.questionsConfig.setExperiment(self.experiment)
		self.questionsConfig.setMainController(self)

	@objc.IBAction
	def startExperiment_(self, sender):
		self.close()
		self.answer.setExperiment(self.experiment)
		self.answer.initWithWindowNibName_('answer')
		self.answer.showWindow_(self.answer)
		

	@objc.IBAction
	def exit_(self, sender):
		self.close()
		from PyObjCTools import AppHelper
		AppHelper.stopEventLoop()
