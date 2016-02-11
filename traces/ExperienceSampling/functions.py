# -*- coding: utf-8 -*-


def displayRule(rule):
	print "Rule:"
	print "Question ununciated: " + rule.question.ununciated
	print "event: " + rule.event.detail
	print "condition: " + rule.condition.detail

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

def displayExperiment(exp):
	for i in range(0, len(exp.questions)):
		displayQuestion(exp.questions[i])
	for j in range(0, len(exp.rules)):
		displayRule(exp.rules[j])