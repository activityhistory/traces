# -*- coding: utf-8 -*-

from Question import Question

class Experiment:

	def __init__(self):
		self.questions = []
		self.rules = []

	##### Counts #####
	def countQuestions(self):
		return len(self.questions)

	def countRules(self):
		return len(self.rules)

	##### Questions methods #####
	def addQuestion(self, question):
		self.questions.append(question)

	def modifyQuestion(self, question, i):
		self.questions[i] = question

	def deleteQuestion(self, i):
		del self.questions[i]

	##### Rules methods #####
	def addRule(self, rule):
		self.rules.append(rule)

	def modifyRule(self, rule, i):
		self.rules[i] = rule

	def deleteRule(self, i):
		del self.rules[i]