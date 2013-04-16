#!/usr/bin/python
# -*- coding: utf-8 -*-

from google.appengine.ext import ndb

class Extension(ndb.Model):
	extID = ndb.StringProperty() # 
	type = ndb.StringProperty() # gadget || robot
	developer = ndb.UserProperty()
	title = ndb.StringProperty()
	description = ndb.TextProperty()
	category = ndb.StringProperty()
	icon = ndb.BlobProperty()
	gadgetURL = ndb.StringProperty()
	robotAddress = ndb.StringProperty()

class Rating(ndb.Model):
	value = ndb.IntegerProperty() # -1 || 1
	extID = ndb.StringProperty()
	user = ndb.UserProperty() # the user who submitted this rating

class User(ndb.Model):
	user = ndb.UserProperty()
	starred = ndb.StringProperty(repeated=True)
