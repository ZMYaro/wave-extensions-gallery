#!/usr/bin/python
# -*- coding: utf-8 -*-

from google.appengine.ext import db

class Extension(db.Model):
	extID = db.StringProperty()
	type = db.StringProperty()
	developer = db.UserProperty()
	title = db.StringProperty()
	description = db.TextProperty()
	gadgetURL = db.StringProperty()

class User(db.Model):
	user = db.UserProperty()
	extensions = db.StringListProperty()
