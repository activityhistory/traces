# -*- coding: utf-8 -*-
import os
import sys
import platform

from setuptools import setup

OPTIONS = {
		'iconfile':'assets/clock.icns',
		'includes' : ['sqlalchemy.dialects.sqlite']
		}

DATA_FILES = ['./assets/clock.png',
			'./assets/clock_grey.png',
			'./assets/cursor.png',
			'./traces/preferences.xib',
			'./traces/experience.xib']

setup(
	name="Traces",
	app=['traces/__init__.py'],
	version='0.9.1',
	setup_requires=["py2app"],
	options={'py2app': OPTIONS},
	data_files=DATA_FILES,
	description= 'Activity Tracker',
	install_requires=[
		"pyobjc-core",
		"pyobjc-framework-Cocoa",
		"pyobjc-framework-Quartz",
		"sqlalchemy",
	]
)
