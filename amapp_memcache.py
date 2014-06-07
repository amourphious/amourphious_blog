import webapp2
import logging
import urllib2

from datetime import datetime, timedelta
from collections import namedtuple

from google.appengine.api import memcache 
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import users

from amapp_db import *
from amapp_misc import *

def set_age(key , val):
	query_time = datetime.utcnow()
	logging.error(val)
	memcache.set(key,(val,query_time))


def get_key(key):
	r = memcache.get(key)
	if r :
		value ,  time = r
		age = (datetime.utcnow() - time ).total_seconds()
	else :
		value , age = None , 0
		
	return value , age


def get_post(update = False):
	r = db.GqlQuery('select * from Blog_Entry order by "created" desc ')
	r = list(r)
	return r , 0
	"""key = "BLOGS"
	d = memcache.get(key)
	logging.error(key + str(d))
	if d is None : 
		r = db.GqlQuery('select * from Blog_Entry order by "created" desc ')
		r = list(r)
		set_age(key , r)
		logging.error("Db query")
		memcache.add(key,(r , datetime.utcnow()))
		return r , 0
	if update :
		r = db.GqlQuery('select * from Blog_Entry order by "created" desc ')
		r = list(r)
		set_age(key , r)
		logging.error("Db query")
		memcache.add(key,(r , datetime.utcnow()))
		return r , 0

	value , age = get_key(key)
	logging.error("cached " + str(int(age)) + " s ago")
	return value , age"""

def get_tags(update = False):
	r = db.GqlQuery('select * from Blog_tags')
	r = list(r)
	return r , 0
	"""key = "TAGS"
	d = memcache.get(key)
	logging.error(key + str(d))
	if d is None:
		r = db.GqlQuery('select * from Blog_tags')
		r = list(r)
		set_age(key , r)
		logging.error("DBQUERY")
		memcache.add(key,(r , datetime.utcnow()))
		return r , 0
	
	if update:
		r = db.GqlQuery('select * from Blog_tags')
		r = list(r)
		set_age(key , r)
		logging.error("DBQUERY")
		memcache.add(key,(r , datetime.utcnow()))
		return r , 0
		
	value ,  age = get_key(key)
	logging.error("cached " + str(int(age)) + " s ago")
	return value , age"""
	
def get_comments(blog_id , update = False):
	r = db.GqlQuery("select * from Blog_comments where blog_id = '"+blog_id+"'")
	r = list(r)
	return r , 0
	"""key = "Post _" + blog_id
	d = memcache.get(key)
	logging.error(key + str(d))
	if d is None:
		r = db.GqlQuery("select * from Blog_comments where blog_id = '"+blog_id+"'")
		r = list(r)
		set_age(key , r)
		logging.error("DB QUERY")
		memcache.add(key,(r , datetime.utcnow()))
		return r , 0
	if update :
		r = db.GqlQuery("select * from Blog_comments where blog_id = '"+blog_id+"'")
		r = list(r)
		set_age(key , r)
		logging.error("DB QUERY")
		memcache.add(key,(r , datetime.utcnow()))
		return r , 0
		
	value , age = get_key(key)
	logging.error("cached " +str(int(age)) + " s ago")
	return value , age"""


def get_troll_img(img_id , update = True) :
	r = db.get(img_id)
	return r , 0
	"""a = img_id
	key = "troll_" + str(a)
	d = memcache.get(key)
	logging.error(key + str(d))
	if d is None:
		r = db.get(img_id)
		set_age(key , r)
		logging.error("DBQUERY")
		logging.error("Db query")
		memcache.add(key,(r , datetime.utcnow()))
		return r , 0
	
	if update :
		r = db.get(img_id)
		set_age(key , r)
		logging.error("DBQUERY")
		logging.error("Db query")
		memcache.add(key,(r , datetime.utcnow()))
		return r , 0
	
	value , age = get_key(key)
	logging.error("cached " + str(int(age)) + " s ago")
	return value , age"""
