# -*- coding: utf-8 -*-

class Answer:
	"""
	object containing the question,
	the time at we submitted the answer
	and the answer value
	"""

	def __init__(self, question = ""):
		self.question = question
		self.time = ""
		self.value = ""