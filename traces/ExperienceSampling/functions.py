# -*- coding: utf-8 -*-

def displayQuestion(question):
	print "Question:"
	print "ununciated: " + question.ununciated
	print "type: " + str(question.type)
	if question.type == 2 :
		if len(question.choices) == 0 :
			print "No choices submitted"
		else :
			print "Choices:"
			for i in range(0, len(question.choices)) :
				print "\t" + question.choices[i]