# -*- coding: utf-8 -*-

from Question import Question

class Event:

	def __init__(self, rule):
		self.rule = rule
		self.type = 0
		self.randomShortcut = [1,1]
		self.detail = ""
		

class Rule:
	"""
	event: 0 = None
		   1 = Random
		   2 = App				2.1 = Safari
		   						2.2 = Email
		   
		   3 = Key Shortcut		3.1 = Cmd + V
		   						3.2 = Cmd + Z
		   						3.3 = Cmd + N
	"""

	def __init__(self):
		self._question = Question()
		self._event = Event(self)
		self._wait = False
		self._timeToWait = "00:00"

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

	def wait():
	    doc = "The wait property."
	    def fget(self):
	        return self._wait
	    def fset(self, value):
	        self._wait = value
	    def fdel(self):
	        del self._wait
	    return locals()
	wait = property(**wait())

	def timeToWait():
	    doc = "The timeToWait property."
	    def fget(self):
	        return self._timeToWait
	    def fset(self, value):
	        self._timeToWait = value
	    def fdel(self):
	        del self._timeToWait
	    return locals()
	timeToWait = property(**timeToWait())