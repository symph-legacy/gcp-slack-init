#!/usr/bin/env python
# -*- coding: utf-8 -*-


from google.appengine.ext import ndb


class Project(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    project_name = ndb.StringProperty()
    project_id = ndb.StringProperty()
    appengine = ndb.BooleanProperty()
