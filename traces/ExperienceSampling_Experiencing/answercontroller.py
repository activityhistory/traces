# -*- coding: utf-8 -*-

from Cocoa import *
from Foundation import NSObject

from Answer import Answer
import datetime
import json
import os

class AnswerController(NSWindowController):

	"""
	To see connections between Outlets/Actions and the interface:
	- load the corresponding view in XCode
	- Click on Add files and add the corresponding controller
	- Check on the connections investigator

	"""
	
	ununciated = objc.IBOutlet()
	textAnswer = objc.IBOutlet()
	choiceAnswer = objc.IBOutlet()

	choice1 = objc.IBOutlet()
	choice2 = objc.IBOutlet()
	choice3 = objc.IBOutlet()
	choice4 = objc.IBOutlet()

	answerWindow = objc.IBOutlet()
	answersWindow = objc.IBOutlet()
	answersList = objc.IBOutlet()
	showingQuestion = objc.IBOutlet()
	showingAnswer = objc.IBOutlet()
	nbAnswers = objc.IBOutlet()
	modifyButton = objc.IBOutlet()
	deleteButton = objc.IBOutlet()

	shown = False
	answer = Answer()
	handler = None
	idToModify = -1
	idToDelete = -1

	def windowDidLoad(self):
		NSWindowController.windowDidLoad(self)
		self.shown = False
		self.handler = None

	def showSimpleQuestion(self, question, handler, modified = -1):
		self.answer = Answer()
		self.handler = handler
		self.ununciated.setStringValue_(question.ununciated)
		self.ununciated.setHidden_(False)
		self.textAnswer.setStringValue_("")
		self.answerWindow.makeKeyAndOrderFront_(self.answerWindow)
		self.answerWindow.makeMainWindow()
		self.answerWindow.setLevel_(NSFloatingWindowLevel)
		self.shown = True
		if modified != -1:
			self.idToModify = modified

	def showMCQuestion(self, question, handler, modified = -1):
		self.answer = Answer()
		self.handler = handler
		self.ununciated.setStringValue_(question.ununciated)
		self.ununciated.setHidden_(False)

		self.choice1.setTransparent_(True)
		self.choice2.setTransparent_(True)
		self.choice3.setTransparent_(True)
		self.choice4.setTransparent_(True)
		
		for i in range(len(question.choices)):
			exec("self.choice%d.setTitle_('%s')" % (i+1, question.choices[i]))
			exec("self.choice%d.setTransparent_(False)" % (i+1))

		self.answerWindow.makeKeyAndOrderFront_(self.answerWindow)
		self.answerWindow.makeMainWindow()
		self.answerWindow.setLevel_(NSFloatingWindowLevel)
		self.shown = True
		if modified != -1:
			self.idToModify = modified

	def setHandler(self, handler):
		self.handler = handler

	@objc.IBAction
	def submitSimpleAnswer_(self, sender):
		self.answer.question = self.ununciated.stringValue()
		self.answer.time = str(datetime.datetime.now())
		self.answer.value = self.textAnswer.stringValue()
		if self.idToModify == -1:
			self.handler.answers.append(self.answer)
		else:
			self.handler.answers[self.idToModify] = self.answer
			self.idToModify = -1

		self.answerWindow.close()
		self.shown = False
		self.close()
		
	@objc.IBAction
	def submitMCQAnswer_(self, sender):
		self.answer.question = self.ununciated.stringValue()
		self.answer.time = str(datetime.datetime.now())
		self.answer.value = str(self.choiceAnswer.selectedCell().title())
		if self.idToModify == -1:
			self.handler.answers.append(self.answer)
		else:
			self.handler.answers[self.idToModify] = self.answer
			self.idToModify = -1
		
		self.answerWindow.close()
		self.shown = False
		self.close()

	def showAnswers(self, handler):
		self.handler = handler
		self.modifyButton.setTag_(-1)
		self.deleteButton.setTag_(-1)
		self.nbAnswers.setStringValue_(str(len(self.handler.answers)))
		self.answersList.removeAllItems()
		for i in range(len(self.handler.answers)):
			self.answersList.addItemWithObjectValue_("Answer " + str(i+1))

		self.showingQuestion.setHidden_(True)
		self.showingAnswer.setHidden_(True)
		self.answersWindow.makeKeyAndOrderFront_(self.answersWindow)
		self.answersWindow.makeMainWindow()
		self.answersWindow.setLevel_(NSFloatingWindowLevel)

	@objc.IBAction
	def showAnswerDetails_(self, sender):
		if self.answersList.objectValueOfSelectedItem() == "":
			self.showingQuestion.setHidden_(True)
			self.showingQuestion.setStringValue_("")
			self.showingAnswer.setHidden_(True)
			self.showingAnswer.setStringValue_("")

			self.modifyButton.setTag_(-1)
			self.deleteButton.setTag_(-1)
		else:
			id = int(self.answersList.objectValueOfSelectedItem()[-1])-1
			self.answer = self.handler.answers[id]

			self.showingQuestion.setHidden_(False)
			self.showingQuestion.setStringValue_(self.answer.question)
			self.showingAnswer.setHidden_(False)
			self.showingAnswer.setStringValue_(self.answer.value)

			self.modifyButton.setTag_(id)
			self.deleteButton.setTag_(id)

	@objc.IBAction
	def modifyAnswer_(self, sender):
		if sender.tag() != -1:
			self.handler.modifyAnswer(sender.tag())
			self.answersWindow.close()
			self.close()

	@objc.IBAction
	def deleteAnswer_(self, sender):
		if sender.tag() != -1:
			self.handler.deleteAnswer(sender.tag())
			self.answersWindow.close()
			self.close()

	def updateDisplay(self):
		self.nbAnswers.setStringValue_(str(len(self.handler.answers)))

