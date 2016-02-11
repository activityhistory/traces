# -*- coding: utf-8 -*-

from Question import Question

class Experiment:

	def __init__(self):
		self._questions = []
		self._rules = []

	def questions():
	    doc = "The questions property."
	    def fget(self):
	        return self._questions
	    def fset(self, value):
	        self._questions = value
	    def fdel(self):
	        del self._questions
	    return locals()
	questions = property(**questions())

	def rules():
	    doc = "The rules property."
	    def fget(self):
	        return self._rules
	    def fset(self, value):
	        self._rules = value
	    def fdel(self):
	        del self._rules
	    return locals()
	rules = property(**rules())

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