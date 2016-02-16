# -*- coding: utf-8 -*-

from Cocoa import *
from Foundation import NSObject
from questioncontroller import QuestionController
from rulecontroller import RuleController
from answercontroller import AnswerController
from eventhandler import EventHandler
import functions
import json
import sys, os
sys.path.insert(0, '..')

from Model.Experiment import Experiment

class MainController(NSWindowController):

	myWindow = objc.IBOutlet()
	nbQuestions = objc.IBOutlet()
	nbRules = objc.IBOutlet()
	handler = None

	def windowDidLoad(self):
		NSWindowController.windowDidLoad(self)
		self.questionsConfig = QuestionController.alloc().initWithWindowNibName_('Question')
		self.rulesConfig = RuleController.alloc().initWithWindowNibName_('Rule')
		self.experiment = Experiment()

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
	def addRule_(self, sender):
		self.rulesConfig.showWindow_(self.rulesConfig)
		self.rulesConfig.showAddWindow()
		self.rulesConfig.setExperiment(self.experiment)
		self.rulesConfig.setMainController(self)
	
	@objc.IBAction
	def showRules_(self, sender):
		self.rulesConfig.showWindow_(self.rulesConfig)
		self.rulesConfig.showRules()
		self.rulesConfig.setExperiment(self.experiment)
		self.rulesConfig.setMainController(self)

	@objc.IBAction
	def startExperiment_(self, sender):
		configFileName = os.path.expanduser("~") + "/.traces/config.log"
		config = open(configFileName, 'w')
		config.write(functions.dumpJson(self.experiment))
		config.close()
		self.myWindow.orderOut_(self.myWindow)

	@objc.IBAction
	def exit_(self, sender):
		self.close()
		from PyObjCTools import AppHelper
		AppHelper.stopEventLoop()
