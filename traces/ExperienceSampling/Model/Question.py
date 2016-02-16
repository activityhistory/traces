# -*- coding: utf-8 -*-

class Question:
	"""
		class Question:
			- ununciated: string
			- type: 1 for open question, 2 for MCQ
	"""

	def __init__(self, type = 1, choices = []):
		self.ununciated = ""
		self.type = type
		self.choices = choices
		if type == 2 and choices == []:
			raise Exception("Missing choices for a MCQ, please submit them.")

	def __eq__(self, other):
		return self.ununciated == other.ununciated and self.type == other.type