# -*- coding: utf-8 -*-
import json
from Model.Experiment import Experiment
from Model.Question import Question
from Model.Rule import Rule

def displayRule(rule):
	print "Rule:"
	print "Question ununciated: " + rule.question.ununciated
	print "event: " + rule.event.detail

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

def getRulesByEvent(experiment, event):
	rules = []
	for i in range(0, experiment.countRules()):
		if experiment.rules[i].event.type == event :
			rules.append(experiment.rules[i])

	return rules

def dumpJson(experiment):
	output = ""
	output += "{"
	output += '"questions": ['
	for i in range(len(experiment.questions)):
		output += json.dumps(experiment.questions[i], default=lambda o: o.__dict__, check_circular=False)
		if i < len(experiment.questions)-1 :
			output += ','
	output += "],"
	output += '"rules": ['
	for i in range(len(experiment.rules)):
		output += '{'
		output += '"question": '
		output += json.dumps(experiment.rules[i].question, default=lambda o: o.__dict__, check_circular=False) + ','
		output += '"event": '
		output += '{'
		output += '"rule": "self",'
		output += '"type": "' + str(experiment.rules[i].event.type) + '",'
		output += '"randomShortcut": "' + str(experiment.rules[i].event.randomShortcut) + '",'
		output += '"detail": "' + experiment.rules[i].event.detail + '"' 
		output += '},'
		output += '"wait": "' + str(experiment.rules[i].wait) + '",'
		output += '"timeToWait": "' + experiment.rules[i].timeToWait + '"'
		output += "}"
		if i < len(experiment.rules)-1 :
			output += ','
	output += "]"
	output += "}"

	return output

def loadJson(data):
	try:
		tempExp = Experiment()
		for i in range(len(data["questions"])):
			tempQuestion = Question()
			tempQuestion.ununciated = str(data["questions"][i]["ununciated"])
			tempQuestion.type = int(data["questions"][i]["type"])
			tempQuestion.choices = data["questions"][i]["choices"]
			tempExp.addQuestion(tempQuestion)
		for i in range(len(data["rules"])):
			tempRule = Rule()
			tempRule.question = Question()
			tempRule.question.ununciated = str(data["rules"][i]["question"]["ununciated"])
			tempRule.question.type = int(data["rules"][i]["question"]["type"])
			tempRule.question.choices = data["rules"][i]["question"]["choices"]

			tempRule.event.type = int(data["rules"][i]["event"]["type"])
			tempRule.event.detail = str(data["rules"][i]["event"]["detail"])
			tempRule.event.randomShortcut = data["rules"][i]["event"]["randomShortcut"]

			tempRule.wait = bool(data["rules"][i]["wait"])
			tempRule.timeToWait =  str(data["rules"][i]["timeToWait"])

			tempExp.addRule(tempRule)

		return tempExp

	except IOError:
		print "Could not open file: " + filename

	except ValueError:
		print "could not create JSON data"
