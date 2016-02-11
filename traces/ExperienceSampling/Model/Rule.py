# -*- coding: utf-8 -*-

from Question import Question

class Event:

	def __init__(self, rule):
		self.rule = rule
		self.type = 0
		self.detail = ""

class Condition:

	def __init__(self, rule):
		self.rule = rule
		self.type = 0
		self.detail = ""
		self.time = "00:00"

class Rule:
	"""
	event: 0 = None
		   1 = Random
		   2 = Email
		   3 = Key Shortcut

	condition: 0 = None
			   1 = Idle
			   2 = Event triggered since
			   3 = Elapsed time since last question
			   4 = No fullscreen
	"""

	def __init__(self):
		self._question = Question()
		self._event = Event(self)
		self._condition = Condition(self)

	def question():
	    doc = "The question property."
	    def fget(self):
	        return self._question
	    def fset(self, value):
	        self._question = value
	    def fdel(self):
	        del self._question
	    return locals()
	question = property(**question())

	def event():
	    doc = "The event property."
	    def fget(self):
	        return self._event
	    def fset(self, value):
	        self._event = value
	    def fdel(self):
	        del self._event
	    return locals()
	event = property(**event())

	def condition():
	    doc = "The condition property."
	    def fget(self):
	        return self._condition
	    def fset(self, value):
	        self._condition = value
	    def fdel(self):
	        del self._condition
	    return locals()
	condition = property(**condition())

	def time():
	    doc = "The time property."
	    def fget(self):
	        return self._time
	    def fset(self, value):
	        self._time = value
	    def fdel(self):
	        del self._time
	    return locals()
	time = property(**time())