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
	stepperMinutes = objc.IBOutlet()
	stepperSeconds = objc.IBOutlet()
	timeMinutes = objc.IBOutlet()
	timeSeconds = objc.IBOutlet()
	eventApp = objc.IBOutlet()
	eventAppPopover = objc.IBOutlet()
	eventShortcut = objc.IBOutlet()
	eventShortcutPopover = objc.IBOutlet()

	randomShortcut = objc.IBOutlet()
	randomContainer = objc.IBOutlet()
	randomOne = objc.IBOutlet()
	stepperRandomOne = objc.IBOutlet()
	randomTwo = objc.IBOutlet()
	stepperRandomTwo = objc.IBOutlet()

	timeBefore = objc.IBOutlet()
	timeBeforePopover = objc.IBOutlet()
	addRuleButton = objc.IBOutlet()

	showRulesWindow = objc.IBOutlet()
	rules = objc.IBOutlet()
	questionUnunciated = objc.IBOutlet()
	eventType = objc.IBOutlet()
	timeToWait = objc.IBOutlet()
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
		self.tempRule = Rule()
		self.addRuleButton.setTag_(-1)
		self.editWindow.setTitle_("Add Rule")
		self.addRuleButton.setTitle_("Add Rule")
		self.question.removeAllItems()
		self.question.addItemWithObjectValue_("")
		for i in range(0, len(self.experiment.questions)) :
			self.question.addItemWithObjectValue_("Question " + str(i+1) + ": " + self.experiment.questions[i].ununciated[0:20] + " ...")

		self.question.selectItemWithObjectValue_("")
		self.event.selectItemWithObjectValue_("")
		self.eventApp.selectItemWithObjectValue_("")
		self.eventShortcut.selectItemWithObjectValue_("")
		self.event.setEnabled_(False)
		self.timeBefore.setEnabled_(False)
		self.randomContainer.setHidden_(True)

		self.editWindow.makeKeyAndOrderFront_(self.editWindow)

	@objc.IBAction
	def choosingQuestion_(self, sender):
		if self.question.objectValueOfSelectedItem() != "":
			self.event.setEnabled_(True)

	@objc.IBAction
	def choosingEvent_(self, sender):
		if self.event.objectValueOfSelectedItem() == "Opening App":
			self.eventShortcutPopover.performClose_(self.eventShortcutPopover)
			self.eventAppPopover.showRelativeToRect_ofView_preferredEdge_(sender.bounds(), sender, NSMaxXEdge)
		elif self.event.objectValueOfSelectedItem() == "Key Shortcut":
			self.eventAppPopover.performClose_(self.eventAppPopover)
			self.eventShortcutPopover.showRelativeToRect_ofView_preferredEdge_(sender.bounds(), sender, NSMaxXEdge)

		if self.event.objectValueOfSelectedItem() != "Random":
			self.timeBefore.setEnabled_(True)

	@objc.IBAction
	def settingRandomShortcut_(self, sender):
		self.randomOne.setStringValue_(self.stepperRandomOne.stringValue())
		self.randomTwo.setStringValue_(self.stepperRandomTwo.stringValue())

		if self.randomShortcut.selectedCell().title() == 'Yes':
			self.randomContainer.setHidden_(False)
		elif self.randomShortcut.selectedCell().title() == 'No':
			self.randomContainer.setHidden_(True)
		
	@objc.IBAction
	def defineRandomOne_(self, sender):
		if self.stepperRandomOne.intValue() > self.stepperRandomTwo.intValue():
			self.stepperRandomOne.setIntValue_(self.stepperRandomTwo.intValue())
		elif self.stepperRandomOne.intValue() < 1:
			self.stepperRandomOne.setIntValue_(1)

		self.randomOne.setStringValue_(self.stepperRandomOne.stringValue())

	@objc.IBAction
	def defineRandomTwo_(self, sender):
		if self.stepperRandomTwo.intValue() < 1:
			self.stepperRandomTwo.setIntValue_(1)
			
		self.randomTwo.setStringValue_(self.stepperRandomTwo.stringValue())

	@objc.IBAction
	def timeBeforeAskingQuestion_(self, sender):
		self.timeMinutes.setStringValue_(self.stepperMinutes.stringValue() + " Min")
		self.timeSeconds.setStringValue_(self.stepperSeconds.stringValue() + " Sec")
		self.timeBeforePopover.showRelativeToRect_ofView_preferredEdge_(sender.bounds(), sender, NSMaxXEdge)

	@objc.IBAction
	def defineTimeMinutes_(self, sender):
		self.timeMinutes.setStringValue_(self.stepperMinutes.stringValue() + " Min")

	@objc.IBAction
	def defineTimeSeconds_(self, sender):
		self.timeSeconds.setStringValue_(self.stepperSeconds.stringValue() + " Sec")

	@objc.IBAction
	def addRule_(self, sender):
		if self.question.objectValueOfSelectedItem() != "" and self.event.objectValueOfSelectedItem() != "" and \
		(self.eventApp.objectValueOfSelectedItem() != "" or self.eventShortcut.objectValueOfSelectedItem() != ""): 
			id = int(self.question.objectValueOfSelectedItem()[9:10])-1
			self.tempRule.question = self.experiment.questions[id]

			if self.event.objectValueOfSelectedItem() == "Random":
				self.tempRule.event.type = 1
				self.tempRule.event.detail = str(self.event.objectValueOfSelectedItem())
			elif self.event.objectValueOfSelectedItem() == "Opening App":
				self.tempRule.event.type = 2
				self.tempRule.event.detail = str(self.event.objectValueOfSelectedItem()) + ": " + str(self.eventApp.objectValueOfSelectedItem())
			elif self.event.objectValueOfSelectedItem() == "Key Shortcut":
				self.tempRule.event.type = 3
				self.tempRule.event.detail = str(self.event.objectValueOfSelectedItem()) + ": " + str(self.eventShortcut.objectValueOfSelectedItem())
				self.tempRule.event.random[0] = int(self.randomOne.stringValue())
				self.tempRule.event.random[1] = int(self.randomTwo.stringValue())

			if self.timeBefore.selectedCell().title() == "Yes":
				self.tempRule.wait = True
				self.tempRule.time = self.stepperMinutes.stringValue() + ":" + self.stepperSeconds.stringValue()

			if self.addRuleButton.tag() == -1:
				self.experiment.addRule(self.tempRule)
			else:
				self.experiment.modifyRule(self.tempRule, self.addRuleButton.tag())

			self.main.updateDisplay()
			self.editWindow.orderOut_(self.editWindow)

	def showRules(self):
		self.rules.removeAllItems()
		self.rules.addItemWithObjectValue_("")
		self.questionUnunciated.setHidden_(True)
		self.eventType.setHidden_(True)
		self.timeToWait.setHidden_(True)
		for i in range(0, len(self.experiment.rules)):
			self.rules.addItemWithObjectValue_("Rule " + str(i+1))

		self.rules.selectItemWithObjectValue_("")
		self.showRulesWindow.makeKeyAndOrderFront_(self.showRules)

	@objc.IBAction
	def showRuleDetails_(self, sender):
		if self.rules.objectValueOfSelectedItem() == "":
			self.questionUnunciated.setStringValue_("")
			self.questionUnunciated.setHidden_(True)
			self.eventType.setHidden_(True)
			self.timeToWait.setHidden_(True)

			self.modifyButton.setTag_(-1)
			self.deleteButton.setTag_(-1)
		else:
			id = int(self.rules.objectValueOfSelectedItem()[5:6])-1
			self.tempRule = self.experiment.rules[id]
			self.questionUnunciated.setStringValue_(self.tempRule.question.ununciated)
			self.questionUnunciated.setHidden_(False)
			self.eventType.setStringValue_(self.tempRule.event.detail)
			self.eventType.setHidden_(False)
			if self.tempRule.time != "None":
				self.timeToWait.setStringValue_(self.tempRule.time.split(':')[0] + " min and " + self.tempRule.time.split(':')[1] + " sec")
			else:
				self.timeToWait.setStringValue_(self.tempRule.time)

			self.timeToWait.setHidden_(False)

			self.modifyButton.setTag_(id)
			self.deleteButton.setTag_(id)

	@objc.IBAction
	def modifyRule_(self, sender):
		if sender.tag() != -1:
			self.editWindow.setTitle_("Modify Rule")
			self.addRuleButton.setTitle_("Modify Rule")
			self.tempRule = self.experiment.rules[sender.tag()]
			self.showRulesWindow.orderOut_(self.showRulesWindow)
			self.question.removeAllItems()
			self.question.addItemWithObjectValue_("")
			for i in range(0, len(self.experiment.questions)) :
				self.question.addItemWithObjectValue_("Question " + str(i+1) + ": " + self.experiment.questions[i].ununciated[0:20] + " ...")

			self.question.selectItemAtIndex_(sender.tag()+1)
			self.event.selectItemAtIndex_(self.tempRule.event.type)
			if self.event.objectValueOfSelectedItem() == "Opening App":
				self.eventApp.selectItemWithObjectValue_(self.tempRule.event.detail.split(': ')[1])
			elif self.event.objectValueOfSelectedItem() == "Key Shortcut":
				self.eventShortcut.selectItemWithObjectValue_(self.tempRule.event.detail.split(': ')[1])
				if self.tempRule.event.random == [1,1]:
					self.randomShortcut.setState_atRow_column_(NSOnState, 0, 1)
					self.randomShortcut.setState_atRow_column_(NSOffState, 0, 0)
				else:
					self.randomShortcut.setState_atRow_column_(NSOnState, 0, 0)
					self.randomShortcut.setState_atRow_column_(NSOffState, 0, 1)

			if self.tempRule.wait == True:
				self.timeBefore.setState_atRow_column_(NSOnState, 0, 1)
				self.timeBefore.setState_atRow_column_(NSOffState, 0, 0)
				self.stepperMinutes.setIntValue_(int(self.tempRule.time.split(":")[0]))
				self.stepperMinutes.setIntValue_(int(self.tempRule.time.split(":")[1]))
			else:
				self.timeBefore.setState_atRow_column_(NSOnState, 0, 0)
				self.timeBefore.setState_atRow_column_(NSOffState, 0, 1)

			self.addRuleButton.setTag_(sender.tag())
			self.editWindow.makeKeyAndOrderFront_(self.editWindow)

	@objc.IBAction
	def deleteRule_(self, sender):
		if sender.tag() != -1:
			self.experiment.deleteRule(sender.tag())
			self.main.updateDisplay()
			self.showRulesWindow.orderOut_(self.showRulesWindow)