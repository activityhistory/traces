# -*- coding: utf-8 -*-
from Cocoa import *
from Foundation import NSObject

import sys
sys.path.insert(0, '..')
from Model.Experiment import Experiment
from Model.Rule import Rule

class RuleController(NSWindowController):

	editWindow = objc.IBOutlet()
	question = objc.IBOutlet()
	event = objc.IBOutlet()
	condition = objc.IBOutlet()
	stepperMinutes = objc.IBOutlet()
	stepperSeconds = objc.IBOutlet()
	timeMinutes = objc.IBOutlet()
	timeSeconds = objc.IBOutlet()
	eventApp = objc.IBOutlet()
	eventAppPopover = objc.IBOutlet()
	eventShortcut = objc.IBOutlet()
	eventShortcutPopover = objc.IBOutlet()
	conditionButton = objc.IBOutlet()
	conditionPopover = objc.IBOutlet()
	addRuleButton = objc.IBOutlet()

	showRulesWindow = objc.IBOutlet()
	rules = objc.IBOutlet()
	questionUnunciated = objc.IBOutlet()
	eventType = objc.IBOutlet()
	conditionType = objc.IBOutlet()
	modifyButton = objc.IBOutlet()
	deleteButton = objc.IBOutlet()

	def windowDidLoad(self):
		NSWindowController.windowDidLoad(self)
		self.experiment = Experiment()
		self.tempRule = Rule()
		self.main = None

	def setExperiment(self, exp):
		self.experiment = exp

	def setMainController(self, main):
		self.main = main

	def showAddWindow(self):
		self.addRuleButton.setTag_(-1)
		self.question.removeAllItems()
		self.question.addItemWithObjectValue_("")
		for i in range(0, len(self.experiment.questions)) :
			self.question.addItemWithObjectValue_("Question " + str(i+1) + ": " + self.experiment.questions[i].ununciated[0:20] + " ...")

		self.question.selectItemWithObjectValue_("")
		self.event.selectItemWithObjectValue_("")
		self.event.setEnabled_(False)
		self.condition.selectItemWithObjectValue_("")
		self.conditionButton.setEnabled_(False)

		self.editWindow.makeKeyAndOrderFront_(self.editWindow)

	@objc.IBAction
	def choosingQuestion_(self, sender):
		self.event.setEnabled_(True)
		self.conditionButton.setEnabled_(True)

	@objc.IBAction
	def choosingEvent_(self, sender):
		if self.event.objectValueOfSelectedItem() == "Opening App":
			self.eventShortcutPopover.performClose_(self.eventShortcutPopover)
			self.eventAppPopover.showRelativeToRect_ofView_preferredEdge_(sender.bounds(), sender, NSMaxXEdge)
		elif self.event.objectValueOfSelectedItem() == "Key Shortcut":
			self.eventAppPopover.performClose_(self.eventAppPopover)
			self.eventShortcutPopover.showRelativeToRect_ofView_preferredEdge_(sender.bounds(), sender, NSMaxXEdge)

	@objc.IBAction
	def choosingCondition_(self, sender):
		self.timeMinutes.setStringValue_(self.stepperMinutes.stringValue() + " Min")
		self.timeSeconds.setStringValue_(self.stepperSeconds.stringValue() + " Sec")
		self.conditionPopover.showRelativeToRect_ofView_preferredEdge_(sender.bounds(), sender, NSMaxXEdge)

	@objc.IBAction
	def fullscreenCondition_(self, sender):
		if self.condition.objectValueOfSelectedItem() == "No fullscreen":
			self.timeMinutes.setEnabled_(False)
			self.stepperMinutes.setEnabled_(False)
			self.timeSeconds.setEnabled_(False)
			self.stepperSeconds.setEnabled_(False)
		else :
			self.timeMinutes.setEnabled_(True)
			self.stepperMinutes.setEnabled_(True)
			self.timeSeconds.setEnabled_(True)
			self.stepperSeconds.setEnabled_(True)


	@objc.IBAction
	def defineTimeMinutes_(self, sender):
		self.timeMinutes.setStringValue_(self.stepperMinutes.stringValue() + " Min")

	@objc.IBAction
	def defineTimeSeconds_(self, sender):
		self.timeSeconds.setStringValue_(self.stepperSeconds.stringValue() + " Sec")

	@objc.IBAction
	def addRule_(self, sender):
		if self.question.objectValueOfSelectedItem() != "" and self.event.objectValueOfSelectedItem() != "" and self.condition.objectValueOfSelectedItem() != "" : 
			id = int(self.question.objectValueOfSelectedItem()[9:10])-1
			self.tempRule.question = self.experiment.questions[id]

			if self.event.objectValueOfSelectedItem() == "Random":
				self.tempRule.event.type = 1
			elif self.event.objectValueOfSelectedItem() == "Opening App":
				self.tempRule.event.type = 2
				self.tempRule.event.detail = str(self.eventApp.objectValueOfSelectedItem())
			elif self.event.objectValueOfSelectedItem() == "Key Shortcut":
				self.tempRule.event.type = 3
				self.tempRule.event.detail = str(self.eventApp.objectValueOfSelectedItem())

			self.tempRule.event.detail = self.event.objectValueOfSelectedItem()

			if self.condition.objectValueOfSelectedItem() == "Idle":
				self.tempRule.condition.type = 1
			elif self.condition.objectValueOfSelectedItem() == "Event triggered since":
				self.tempRule.condition.type = 2
			elif self.condition.objectValueOfSelectedItem() == "Elapsed time since last question":
				self.tempRule.condition.type = 3
			elif self.condition.objectValueOfSelectedItem() == "No fullscreen":
				self.tempRule.condition.type = 4

			self.tempRule.condition.detail = self.condition.objectValueOfSelectedItem()
			self.tempRule.condition.time = str(self.stepperMinutes.stringValue()) + ":" + str(self.stepperSeconds.stringValue())

			if self.addRuleButton.tag() == -1:
				self.experiment.addRule(self.tempRule)
			else:
				self.experiment.modifyRule(self.tempRule, addRuleButton.tag())

			self.main.updateDisplay()
			self.editWindow.orderOut_(self.editWindow)

	def showRules(self):
		self.rules.removeAllItems()
		self.rules.addItemWithObjectValue_("")
		self.questionUnunciated.setStringValue_("")
		self.questionUnunciated.setHidden_(True)
		self.eventType.setStringValue_("")
		self.eventType.setHidden_(True)
		self.conditionType.setStringValue_("")
		self.conditionType.setHidden_(True)

		for i in range(0, len(self.experiment.rules)):
			self.rules.addItemWithObjectValue_("Rule " + str(i+1))

		self.rules.selectItemWithObjectValue_("")
		self.showRulesWindow.makeKeyAndOrderFront_(self.showRules)

	@objc.IBAction
	def showRuleDetails_(self, sender):
		if self.rules.objectValueOfSelectedItem() == "":
			self.questionUnunciated.setStringValue_("")
			self.questionUnunciated.setHidden_(True)
			self.eventType.setStringValue_("")
			self.eventType.setHidden_(True)
			self.conditionType.setStringValue_("")
			self.conditionType.setHidden_(True)

			self.modifyButton.setTag_(-1)
			self.deleteButton.setTag_(-1)
		else:
			id = int(self.rules.objectValueOfSelectedItem()[5:6])-1
			self.tempRule = self.experiment.rules[id]
			self.questionUnunciated.setStringValue_(self.tempRule.question.ununciated)
			self.questionUnunciated.setHidden_(False)
			self.eventType.setStringValue_(self.tempRule.event.detail)
			self.eventType.setHidden_(False)
			self.conditionType.setStringValue_(self.tempRule.condition.detail)
			self.conditionType.setHidden_(False)

			self.modifyButton.setTag_(id)
			self.deleteButton.setTag_(id)

	@objc.IBAction
	def modifyRule_(self, sender):
		if sender.tag() != -1:
			self.tempRule = self.experiment.rules[sender.tag()]
			self.showRulesWindow.orderOut_(self.showRulesWindow)
			self.question.removeAllItems()
			self.question.addItemWithObjectValue_("")
			for i in range(0, len(self.experiment.questions)) :
				self.question.addItemWithObjectValue_("Question " + str(i+1) + ": " + self.experiment.questions[i].ununciated[0:20] + " ...")

			self.question.selectItemAtIndex_(sender.tag()+1)
			self.event.selectItemAtIndex_(self.tempRule.event.type)
			self.condition.selectItemAtIndex_(self.tempRule.condition.type)
			self.addRuleButton.setTag_(sender.tag())
			self.editWindow.makeKeyAndOrderFront_(self.editWindow)

	@objc.IBAction
	def deleteRule_(self, sender):
		if sender.tag() != -1:
			self.experiment.deleteRule(sender.tag())
			self.main.updateDisplay()
			self.showRulesWindow.orderOut_(self.showRulesWindow)