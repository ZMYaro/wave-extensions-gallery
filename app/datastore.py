#!/usr/bin/python
# -*- coding: utf-8 -*-

from google.appengine.ext import db

class Extension(db.Model):
	extID = db.StringProperty() # 
	type = db.StringProperty() # gadget || robot
	developer = db.UserProperty()
	title = db.StringProperty()
	description = db.TextProperty()
	category = db.StringProperty()
	icon = db.BlobProperty()
	gadgetURL = db.LinkProperty()
	robotAddress = db.EmailProperty()

class Rating(db.Model):
	value = db.IntegerProperty() # -1 || 1
	extID = db.StringProperty()
	voter = db.UserProperty() # the user who submitted this rating

class User(db.Model):
	user = db.UserProperty()
	starred = db.StringListProperty()
