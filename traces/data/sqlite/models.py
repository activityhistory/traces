# -*- coding: utf-8 -*-
"""
Traces: Activity Tracker
Copyright (C) 2015 Adam Rule
with Aurélien Tabard, Jonas Keper, Azeem Ghumman, and Maxime Guyaux

Inspired by Selfspy and Burrito
https://github.com/gurgeh/selfspy
https://github.com/pgbovine/burrito/

You should have received a copy of the GNU General Public License
along with Traces. If not, see <http://www.gnu.org/licenses/>.
"""

import zlib
import json

import datetime

from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import (Index, Column, Boolean, Integer, Unicode, Binary,
						Float, ForeignKey, create_engine)
from sqlalchemy.orm import sessionmaker, relationship, backref

ENCRYPTER = None
Base = declarative_base()


def initialize(fname):
	engine = create_engine('sqlite:///%s' % fname)
	Base.metadata.create_all(engine)
	return sessionmaker(bind=engine)

# TODO check if having a time for each event will cause issues with matching
# items that are not time based, such as geometries
class Core(object):

	# set the table name to the class name
	@declared_attr
	def __tablename__(cls):
		return cls.__name__.lower()

	# make sure every class has a primary key and time
	id = Column(Integer, primary_key=True)
	time = Column(Float, nullable=False)


class Click(Core, Base):
	button = Column(Integer, nullable=False)
	x = Column(Integer, nullable=False)
	y = Column(Integer, nullable=False)

	app_id = Column(Integer, ForeignKey('app.id'), nullable=False, index=True)
	app = relationship("App", backref=backref('clicks'))

	window_id = Column(Integer, ForeignKey('window.id'), nullable=False)
	window = relationship("Window", backref=backref('clicks'))
	#
	# geometry_id = Column(Integer, ForeignKey('geometry.id'), nullable=False)
	# geometry = relationship("Geometry", backref=backref('clicks'))

	def __init__(self, time, button, x, y, app_id, window_id): #geometry_id):
		self.time = time
		self.button = button
		self.x = x
		self.y = y
		self.app_id = app_id
		self.window_id = window_id
		# self.geometry_id = geometry_id

	def __repr__(self):
		return "<%d Click (%d, %d)>" % (self.button, self.x, self.y)


class Keys(Core, Base):
	key = Column(Unicode, index=True)
	modifiers = Column(Unicode, index=True)

	app_id = Column(Integer, ForeignKey('app.id'), nullable=False, index=True)
	app = relationship("App", backref=backref('keys'))

	window_id = Column(Integer, ForeignKey('window.id'), nullable=False)
	window = relationship("Window", backref=backref('keys'))

	# geometry_id = Column(Integer, ForeignKey('geometry.id'), nullable=False)
	# geometry = relationship("Geometry", backref=backref('keys'))

	def __init__(self, time, key, modifiers, app_id, window_id): #, geometry_id):
		self.time = time
		self.key = key
		self.modifiers = modifiers
		self.app_id = app_id
		self.window_id = window_id
		# self.geometry_id = geometry_id
		# self.started = started


	def __repr__(self):
		return "<Key %s>" % self.key


class Move(Core, Base):
	x = Column(Integer, nullable=False)
	y = Column(Integer, nullable=False)

	def __init__(self, time, x, y):
		self.time = time
		self.x = x
		self.y = y

	def __repr__(self):
		return "<%d Move (%d, %d)>" % (self.x, self.y)


# TODO add tracking of which window was scrolled
class Scroll(Core, Base):
	x = Column(Integer, nullable=False)
	y = Column(Integer, nullable=False)

	app_id = Column(Integer, ForeignKey('app.id'), nullable=False, index=True)
	app = relationship("App", backref=backref('scroll'))

	window_id = Column(Integer, ForeignKey('window.id'), nullable=False)
	window = relationship("Window", backref=backref('scroll'))

	def __init__(self, time, x, y, app_id, window_id):
		self.time = time
		self.x = x
		self.y = y
		self.app_id = app_id
		self.window_id = window_id

	def __repr__(self):
		return "<%d Scroll (%d, %d)>" % (self.x, self.y)


class App(Core, Base):
	name = Column(Unicode, index=True, unique=True)

	def __init__(self, time, name):
		self.time = time
		self.name = name

	def __repr__(self):
		return "<App '%s'>" % self.name


class AppEvent(Core, Base):
	event = Column(Unicode, index=True)

	app_id = Column(Integer, ForeignKey('app.id'), nullable=False, index=True)
	app = relationship("App", backref=backref('appevents'))

	def __init__(self, time, app_id, event):
		self.time = time
		self.event = event
		self.app_id = app_id

	def __repr__(self):
		return "<App '%s' '%s' >" % (self.app_id, self.event)


class Window(Core, Base):
	title = Column(Unicode, index=True)

	app_id = Column(Integer, ForeignKey('app.id'), nullable=False, index=True)
	app = relationship("App", backref=backref('windows'))

	def __init__(self, time, app_id, title):
		self.time = time
		self.app_id = app_id
		self.title = title

	def __repr__(self):
		return "<Window '%s'>" % (self.title)


class WindowEvent(Core, Base):
	event = Column(Unicode, index=True)

	window_id = Column(Integer, ForeignKey('window.id'), nullable=False, index=True)
	window = relationship("Window", backref=backref('windowevents'))

	def __init__(self, time, window_id, event):
		self.time = time
		self.window_id = window_id
		self.event = event

	def __repr__(self):
		return "<Window '%s' '%s' >" % (self.window_id, self.event)


class Geometry(Core, Base):
	x = Column(Integer, nullable=False)
	y = Column(Integer, nullable=False)
	w = Column(Integer, nullable=False)
	h = Column(Integer, nullable=False)

	Index('idx_geo', 'x', 'y', 'w', 'h')

	def __init__(self, time, x, y, w, h):
		self.time = time
		self.x = x
		self.y = y
		self.w = w
		self.h = h

	def __repr__(self):
		return "<Geometry (%d, %d), (%d, %d)>" % (self.x, self.y, self.w, self.h)


class Arrangement(Core, Base):
	arr = Column(Unicode, nullable=False)

	def __init__(self, time, arr):
		self.time = time
		self.arr = arr

	def __repr__(self):
		return "<Arrangement '%s' >" % self.arr


class RecordingEvent(Core, Base):
	event = Column(Unicode, index=True)

	def __init__(self, time, event):
		self.time = time
		self.event = event

	def __repr__(self):
		return "<Recording '%s' >" % self.event


class Experience(Core, Base):
	text = Column(Unicode)

	def __init__(self, time, text):
		self.time = time
		self.text = text

	def __repr__(self):
		return "<Experience '%s' >" % self.text


class Clipboard(Core, Base):
	text = Column(Unicode)
	url = Column(Unicode)
	image = Column(Unicode)

	def __init__(self, time, text, url, image):
		self.time = time
		self.text = text
		self.url = url
		self.image = image

	def __repr__(self):
		return "<Clipboard '%s' >" % self.text

class URL(Core, Base):
	title = Column(Unicode)
	url = Column(Unicode)
	host = Column(Unicode)

	def __init__(self, time, title, url, host):
		self.time = time
		self.title = title
		self.url = url
		self.host = host

	def __repr__(self):
		return "<URL '%s' - '%s'>" % (self.url, self.title)


class URLEvent(Core, Base):
	title = Column(Unicode)

	url_id = Column(Integer, ForeignKey('url.id'), nullable=False, index=True)
	window = relationship("URL", backref=backref('urlevents'))
	app_id = Column(Integer, ForeignKey('app.id'), nullable=False, index=True)
	window = relationship("App", backref=backref('urlevents'))
	window_id = Column(Integer, ForeignKey('window.id'), nullable=False, index=True)
	window = relationship("Window", backref=backref('urlevents'))

	event = Column(Unicode)

	def __init__(self, time, url_id, app_id, window_id, event):
		self.time = time
		self.url_id = url_id
		self.app_id = app_id
		self.window_id = window_id
		self.event = event

	def __repr__(self):
		return "<URLEvent %s %s %s>" % (self.url_id, self.app_id, self.event)
