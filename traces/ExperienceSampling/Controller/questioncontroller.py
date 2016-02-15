# -*- coding: utf-8 -*-
from Cocoa import *
from Foundation import NSObject

import sys
sys.path.insert(0, '..')
from Model.Experiment import Experiment
from Model.Question import Question
import functions
class QuestionController(NSWindowController):

	# windows outlets
	editWindow = objc.IBOutlet()
	questionWindow = objc.IBOutlet()
	
	# Add/Modify question outlets
	questionField = objc.IBOutlet()
	questionType = objc.IBOutlet()
	popover = objc.IBOutlet()
	choice1 = objc.IBOutlet()
	choice2 = objc.IBOutlet()
	choice3 = objc.IBOutlet()
	choice4 = objc.IBOutlet()
	
	# show questions outlets
	questionsList = objc.IBOutlet()
	detailsUnunciated = objc.IBOutlet()
	detailsType = objc.IBOutlet()
	
	# buttons outlets
	submitButton = objc.IBOutlet()
	modifyButton = objc.IBOutlet()
	deleteButton = objc.IBOutlet()

	def windowDidLoad(self):
		NSWindowController.windowDidLoad(self)
		self.experiment = Experiment()
		self.tempQuestion = Question()
		self.main = None

	def setExperiment(self, exp):
		self.experiment = exp

	def setMainController(self, main):
		self.main = main

	def showAddWindow(self):
		self.tempQuestion = Question()
		self.submitButton.setTag_(-1)
		self.questionField.setStringValue_(self.tempQuestion.ununciated)
		self.choice1.setStringValue_("")
		self.choice2.setStringValue_("")
		self.choice3.setStringValue_("")
		self.choice4.setStringValue_("")
		self.editWindow.setTitle_("Add Question")
		self.editWindow.makeKeyAndOrderFront_(self.editWindow)

	def showQuestions(self):
		self.questionsList.removeAllItems()
		self.detailsUnunciated.setStringValue_("")
		self.detailsUnunciated.setHidden_(True)
		self.detailsType.setStringValue_("")
		self.detailsType.setHidden_(True)
		self.questionsList.addItemWithObjectValue_("")
		for i in range(0, len(self.experiment.questions)) :
			self.questionsList.addItemWithObjectValue_("Question " + str(i+1) + ": " + self.experiment.questions[i].ununciated[0:20] + " ...")

		self.questionsList.selectItemWithObjectValue_("")
		self.questionWindow.makeKeyAndOrderFront_(self.questionWindow)

	@objc.IBAction
	def ShowQuestionDetails_(self, sender):
		if self.questionsList.objectValueOfSelectedItem() == "" :
			self.detailsUnunciated.setStringValue_("")
			self.detailsUnunciated.setHidden_(True)
			self.detailsType.setStringValue_("")
			self.detailsType.setHidden_(True)

			self.modifyButton.setTag_(-1)
			self.deleteButton.setTag_(-1)

		else :
			id = int(self.questionsList.objectValueOfSelectedItem()[9:10])-1
			self.tempQuestion = self.experiment.questions[id]
			
			self.detailsUnunciated.setHidden_(False)
			self.detailsType.setHidden_(False)
			self.detailsUnunciated.setStringValue_(self.tempQuestion.ununciated)
			if self.tempQuestion.type == 1:
				self.detailsType.setStringValue_("Open Question")
			else :
				self.detailsType.setStringValue_("MCQ")

			self.modifyButton.setTag_(id)
			self.deleteButton.setTag_(id)
	
	@objc.IBAction
	def modifyQuestion_(self, sender):
		if sender.tag() != -1 :
			self.questionWindow.orderOut_(self.questionWindow)
			self.questionField.setStringValue_(self.tempQuestion.ununciated)
			self.questionType.setState_atRow_column_(NSOnState, self.tempQuestion.type-1, 0)
			if self.tempQuestion.type == 2:
				prefix = "choice"
				for i in range(0, len(self.tempQuestion.choices)-1):
					exec("self.%s%d.setStringValue_('%s')" % (prefix, i+1, self.tempQuestion.choices[i]))

			self.submitButton.setTag_(sender.tag())
			self.editWindow.setTitle_("Modify Question")
			self.editWindow.makeKeyAndOrderFront_(self.editWindow)

	@objc.IBAction
	def deleteQuestion_(self, sender):
		if sender.tag() != -1 :
			self.experiment.deleteQuestion(sender.tag())
			self.main.updateDisplay()
			self.questionWindow.orderOut_(self.questionWindow)

	@objc.IBAction
	def fillChoices_(self, sender):
		self.popover.showRelativeToRect_ofView_preferredEdge_(sender.bounds(), sender, NSMaxXEdge)

	@objc.IBAction
	def addChoices_(self, sender):
		i = 0
		if self.choice1.stringValue() != "" :
			i += 1

		if self.choice2.stringValue() != "" :
			i += 1

		if self.choice3.stringValue() != "" :
			i += 1

		if self.choice4.stringValue() != "" :
			i += 1

		self.tempQuestion.choices = []
		for j in range(i):
			exec("self.tempQuestion.choices.append(str(self.choice%d.stringValue()))" % (j+1))
		
		if i >= 2:
			self.popover.performClose_(self.popover)

	@objc.IBAction
	def submitQuestion_(self, sender):
		if self.questionField.stringValue() != "":
			self.tempQuestion.ununciated = self.questionField.stringValue()
			if self.questionType.selectedCell().title() == 'Open':
				self.tempQuestion.type = 1
			elif self.questionType.selectedCell().title() == 'MCQ':
				self.tempQuestion.type = 2

			if self.tempQuestion.type == 2 and len(self.tempQuestion.choices) < 2:
				self.popover.showRelativeToRect_ofView_preferredEdge_(sender.bounds(), sender, NSMaxXEdge)
			else:
				if self.submitButton.tag() == -1 :
					self.experiment.addQuestion(self.tempQuestion)
				else :
					self.experiment.modifyQuestion(self.tempQuestion, self.submitButton.tag())

				self.main.updateDisplay()
				self.editWindow.orderOut_(self.editWindow)
