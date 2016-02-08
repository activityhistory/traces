# -*- coding: utf-8 -*-

class Question:
	"""
		class Question:
			- ununciated: string
			- type: 1 for open question, 2 for MCQ
	"""

	def __init__(self, type = 1, choices = []):
		self._ununciated = ""
		self._type = type
		self._choices = choices
		if type == 2 and choices == []:
			raise Exception("Missing choices for a MCQ, please submit them.")

	def ununciated():
	    doc = "The ununciated property."
	    def fget(self):
	        return self._ununciated
	    def fset(self, value):
	        self._ununciated = value
	    def fdel(self):
	        del self._ununciated
	    return locals()
	ununciated = property(**ununciated())

	def type():
	    doc = "The type property."
	    def fget(self):
	        return self._type
	    def fset(self, value):
	        self._type = value
	    def fdel(self):
	        del self._type
	    return locals()
	type = property(**type())

	def choices():
	    doc = "The choices property."
	    def fget(self):
	        return self._choices
	    def fset(self, value):
	        self._choices = value
	    def fdel(self):
	        del self._choices
	    return locals()
	choices = property(**choices())

	def __eq__(self, other):
		return self.ununciated == other.ununciated and self.type == other.type