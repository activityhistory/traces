# -*- coding: utf-8 -*-

from Question import Question

class Event:
	"""
	event: 0 = None
		   1 = Random
		   2 = App				2.1 = Safari
		   						2.2 = Email
		   
		   3 = Key Shortcut		3.1 = Cmd + V
		   						3.2 = Cmd + Z
		   						3.3 = Cmd + N
	"""
	def __init__(self, rule):
		self.rule = rule
		self.type = 0
		self.randomShortcut = [1,1]
		self.detail = ""
		

class Rule:
	"""
	Rule: Containing:
	- the question to ask,
	- The event to trigger the question,
	- Time we should wait before asking the question
	"""
	def __init__(self):
		self.question = Question()
		self.event = Event(self)
		self.wait = False
		self.timeToWait = "00:00"