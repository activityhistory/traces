# -*- coding: utf-8 -*-
from Cocoa import *
from Foundation import NSObject

import sys
sys.path.insert(0, '..')
from Model.Experiment import Experiment
from Model.Rule import Rule

class RuleController(NSWindowController):

	"""
	To see connections between Outlets/Actions and the interface:
	- load the corresponding view in XCode
	- Click on Add files and add the corresponding controller
	- Check on the connections investigator

	"""

	#edit window outlets
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

	#Key shortcut random outlets
	randomShortcut = objc.IBOutlet()
	randomContainer = objc.IBOutlet()
	randomOne = objc.IBOutlet()
	stepperRandomOne = objc.IBOutlet()
	randomTwo = objc.IBOutlet()
	stepperRandomTwo = objc.IBOutlet()

	# time before event outlets
	timeBefore = objc.IBOutlet()
	timeBeforePopover = objc.IBOutlet()
	addRuleButton = objc.IBOutlet()

	#show rules window outlets
	showRulesWindow = objc.IBOutlet()
	rules = objc.IBOutlet()
	questionUnunciated = objc.IBOutlet()
	eventType = objc.IBOutlet()
	timeToWait = objc.IBOutlet()
	modifyButton = objc.IBOutlet()
	deleteButton = objc.IBOutlet()

	experiment = Experiment()
	tempRule = Rule()
	main = None

	def windowDidLoad(self):
		NSWindowController.windowDidLoad(self)
		
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
		self.randomShortcut.setState_atRow_column_(NSOnState, 0, 1)
		self.randomShortcut.setState_atRow_column_(NSOffState, 0, 0)
		self.timeBefore.setState_atRow_column_(NSOnState, 0, 0)
		self.timeBefore.setState_atRow_column_(NSOffState, 0, 1)
		self.timeMinutes.setIntValue_(0)
		self.timeSeconds.setIntValue_(0)
		self.event.setEnabled_(False)
		self.timeBefore.setEnabled_(False)
		self.randomContainer.setHidden_(True)

		self.editWindow.makeKeyAndOrderFront_(self.editWindow)

	@objc.IBAction # triggered when we choose a question
	def choosingQuestion_(self, sender):
		if self.question.objectValueOfSelectedItem() != "":
			self.event.setEnabled_(True)

	@objc.IBAction # triggered when choosing an event
	def choosingEvent_(self, sender):
		if self.event.objectValueOfSelectedItem() == "":
			self.timeBefore.setEnabled_(False)
		else:
			self.timeBefore.setEnabled_(True)
			if self.event.objectValueOfSelectedItem() == "Opening App":
				self.eventShortcutPopover.performClose_(self.eventShortcutPopover)
				self.eventAppPopover.showRelativeToRect_ofView_preferredEdge_(sender.bounds(), sender, NSMaxXEdge)
			elif self.event.objectValueOfSelectedItem() == "Key Shortcut":
				self.eventAppPopover.performClose_(self.eventAppPopover)
				self.eventShortcutPopover.showRelativeToRect_ofView_preferredEdge_(sender.bounds(), sender, NSMaxXEdge)

	@objc.IBAction # triggered when choosing a keyboard event
	def settingRandomShortcut_(self, sender):
		self.randomOne.setStringValue_(self.stepperRandomOne.stringValue())
		self.randomTwo.setStringValue_(self.stepperRandomTwo.stringValue())

		if self.randomShortcut.selectedCell().title() == 'Yes':
			self.randomContainer.setHidden_(False)
		elif self.randomShortcut.selectedCell().title() == 'No':
			self.randomContainer.setHidden_(True)
		
	@objc.IBAction # triggered when setting the first value of the random keyboard shortcut
	def defineRandomOne_(self, sender):
		if self.stepperRandomOne.intValue() > self.stepperRandomTwo.intValue():
			self.stepperRandomOne.setIntValue_(self.stepperRandomTwo.intValue())
		elif self.stepperRandomOne.intValue() < 1:
			self.stepperRandomOne.setIntValue_(1)

		self.randomOne.setStringValue_(self.stepperRandomOne.stringValue())

	@objc.IBAction # triggered when setting the second value of the random keyboard shortcut
	def defineRandomTwo_(self, sender):
		if self.stepperRandomTwo.intValue() < 1:
			self.stepperRandomTwo.setIntValue_(1)
			
		self.randomTwo.setStringValue_(self.stepperRandomTwo.stringValue())

	@objc.IBAction # triggered when choosing yes to "time before ..."
	def timeBeforeAskingQuestion_(self, sender):
		self.timeMinutes.setStringValue_(self.stepperMinutes.stringValue() + " Min")
		self.timeSeconds.setStringValue_(self.stepperSeconds.stringValue() + " Sec")
		self.timeBeforePopover.showRelativeToRect_ofView_preferredEdge_(sender.bounds(), sender, NSMaxXEdge)

	@objc.IBAction # triggered when setting the minutes 
	def defineTimeMinutes_(self, sender):
		self.timeMinutes.setStringValue_(self.stepperMinutes.stringValue() + " Min")

	@objc.IBAction # triggered when setting the seconds
	def defineTimeSeconds_(self, sender):
		self.timeSeconds.setStringValue_(self.stepperSeconds.stringValue() + " Sec")

	@objc.IBAction # triggered when clicking on submit
	def addRule_(self, sender):
		#checkin fields
		if self.question.objectValueOfSelectedItem() != "" and self.event.objectValueOfSelectedItem() != "" and \
		(self.eventApp.objectValueOfSelectedItem() != "" or self.eventShortcut.objectValueOfSelectedItem() != "" or \
		self.event.objectValueOfSelectedItem() == "Random"): 
			
			# getting the id of the question
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
				if self.randomShortcut.selectedCell().title() == 'Yes':
					self.tempRule.event.randomShortcut[0] = int(self.randomOne.stringValue())
					self.tempRule.event.randomShortcut[1] = int(self.randomTwo.stringValue())

			if self.timeBefore.selectedCell().title() == "Yes":
				self.tempRule.wait = True
				self.tempRule.timeToWait = self.stepperMinutes.stringValue() + ":" + self.stepperSeconds.stringValue()

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

	@objc.IBAction # triggered when choosing a rule to modify or delete
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
			if self.tempRule.wait != False:
				self.timeToWait.setStringValue_(self.tempRule.timeToWait.split(':')[0] + " min and " + self.tempRule.timeToWait.split(':')[1] + " sec")
			else:
				self.timeToWait.setStringValue_(self.tempRule.timeToWait)

			self.timeToWait.setHidden_(False)

			self.modifyButton.setTag_(id)
			self.deleteButton.setTag_(id)

	@objc.IBAction # triggered when clicking on modify
	def modifyRule_(self, sender):
		# if the tag equals -1 it means that we havent selected a valid rule
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
				if self.tempRule.event.randomShortcut == [1,1]:
					self.randomShortcut.setState_atRow_column_(NSOnState, 0, 1)
					self.randomShortcut.setState_atRow_column_(NSOffState, 0, 0)
				else:
					self.randomShortcut.setState_atRow_column_(NSOnState, 0, 0)
					self.randomShortcut.setState_atRow_column_(NSOffState, 0, 1)

			if self.tempRule.wait == True:
				self.timeBefore.setState_atRow_column_(NSOnState, 0, 1)
				self.timeBefore.setState_atRow_column_(NSOffState, 0, 0)
				self.stepperMinutes.setIntValue_(int(self.tempRule.timeToWait.split(":")[0]))
				self.stepperSeconds.setIntValue_(int(self.tempRule.timeToWait.split(":")[1]))
			else:
				self.timeBefore.setState_atRow_column_(NSOnState, 0, 0)
				self.timeBefore.setState_atRow_column_(NSOffState, 0, 1)
				self.stepperMinutes.setIntValue_(0)
				self.stepperSeconds.setIntValue_(0)

			self.addRuleButton.setTag_(sender.tag())
			self.editWindow.makeKeyAndOrderFront_(self.editWindow)

	@objc.IBAction # triggered when clicking on delete
	def deleteRule_(self, sender):
		if sender.tag() != -1:
			self.experiment.deleteRule(sender.tag())
			self.main.updateDisplay()
			self.showRulesWindow.orderOut_(self.showRulesWindow)