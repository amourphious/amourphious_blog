import webapp2
import cgi
import re
import os
import logging
import jinja2
import random
import string
import hashlib
import urllib2
import json


from xml.dom.minidom import Document
from xml.dom import minidom

from datetime import datetime, timedelta
from collections import namedtuple

from google.appengine.api import mail 
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import users

from amapp_db import *
from amapp_misc import *
from amapp_memcache import *


GMAPS_URL = "http://maps.googleapis.com/maps/api/staticmap?&maptype=roadmap&size=380x263&sensor=false&"


class Intro(Handler):
	def get(self):
		self.render("intro")
		

class MainPage(Handler):
	def get(self):
		password=self.request.cookies.get('u_name','')
		
		if password == "" or password == None:
			un = None
		else:
			lst = password.split('|')
			if len(lst) > 1 :
				un = lst[1]
			else :
				un = None

		self.render("home.html" , username = un)


class AsciiArt(Handler):
	url="http://api.hostip.info/?ip="
	ip="4.2.2.2"
	def getlocation(self,ip):
		self.url+=ip
		try:
			contents=urllib2.urlopen(self.url).read()
		except:
			return
		if contents:
			d=minidom.parseString(contents)
			coords=d.getElementsByTagName("gml:coordinates")
			if coords and coords[0].childNodes[0].nodeValue:
				lon , lat = coords[0].childNodes[0].nodeValue.split(",")
				return db.GeoPt(lat,lon)


	
	def gmaps_img(self,points):
		markers = "&".join("markers=%s,%s"%(p.lat,p.lon)for p in points)
		return GMAPS_URL + markers
		

	def fetch_arts(self,update = False):
		arts = db.GqlQuery("select * from Art order by created desc limit 10")
		arts = list(arts)
		"""key='top'
		arts=memcache.get(key)
		if arts is None or update :
			logging.error("DB QUERY AsciiArt")
			arts=db.GqlQuery("select * from Art order by created desc limit 10")
			arts=list(arts)
			memcache.set(key,arts)"""
		
		return arts
			
			
	def render_aschome(self,title="",error="",art=""):
		arts = self.fetch_arts()
		points = filter(None,(a.coords for a in arts))
		img_url = None
		if points:
			img_url = self.gmaps_img(points)
			#self.write(img_url)
		self.render("asciichan.html",error=error,title=title,art=art,arts=arts,img_url = img_url)
	
	def get(self):
		#self.write(repr(self.getlocation(self.request.remote_addr)))
		#self.write(repr(self.request.remote_addr))
		self.render_aschome()
		
	def post(self):
		title=self.request.get("title")
		art=self.request.get("art")
		troll = self.request.get("troll")
		troll = str(troll)
		coords=self.getlocation(self.request.remote_addr)
		
		if title :
			a=Art(title=title)
			if art :
				a.art = art
			if coords:
				a.coords=coords
			if troll :
				img = db.Blob(troll)
				image = Image(image = img)
				image.put()
				a.troll = str(image.img_key()) 
			
			a.put()
			self.redirect("/asciichan")
		else :
			error="Please provide with both art and title"
			self.render_aschome(title,error,art)

class Disp_img(Handler) :
	def get(self):
		img_id = self.request.get('img_id')
		art , age = get_troll_img(img_id)
		if art.image :
			self.response.headers['Content-Type'] = 'image/png'
			self.response.out.write(art.image)
		else :
			self.write("")

class Signup(Handler):
	
	def write_sup_form(self,error1="",error2="",error3="",error4="",username="",password="",verify="",email=""):
		
		self.render("signup.html",error1=error1,error2=error2,error3=error3,error4=error4,usrnm=escape_html(username),pswrd=escape_html(password),
											vrfy=escape_html(verify),
											mail=escape_html(email))
	def get(self):
		self.write_sup_form()
		
	def post(self):
		username=self.request.get('username')
		password=self.request.get('password')
		verify=self.request.get('verify')
		email=self.request.get('email')
		if(password!=verify):
			error3="password not match"
		else:
			error3=""
		
		if(valid_username(username)):
			error1=""
		else:
			error1="Invalid Username"
		if (valid_password(password)):
			error2=""
		else:
			error2="Invalid Password"
		if(email=="" or valid_email(email)):
			error4=""
		else:
			error4="Invalid E-mail"
		entry=db.GqlQuery("select * from Un_pw where username='"+username+"'")
		for ent in entry:
			error1="user exists"
		
		if not(error1=="" and error2=="" and error3=="" and error4==""):
			self.write_sup_form(error1,error2,error3,error4,username,password,verify,email)
		else:
			pa=make_pw_hash(username,password)
			a=Un_pw(username=username,password=pa)
			a_key=a.put()
			uname=str(pa)
			self.response.headers.add_header('Set-Cookie',"name=%s ; Path=/" % uname)
			self.response.headers.add_header('Set-Cookie',"u_name=%s ; Path=/" % str(hash_str(username)+'|'+username))
			
			self.redirect("/blog/welcome")


			
class Login(Handler):
	
	def write_login_form(self,error="",username="",password=""):
		
		self.render("login",error=error,usrnm=escape_html(username),pswrd=escape_html(password))
	
	def get(self):
		self.write_login_form()
		
	def post(self):
		username=self.request.get('username')
		password=self.request.get('password')
		
		if(valid_username(username) and valid_password):
			entry=db.GqlQuery("select * from Un_pw where username='"+username+"'")
			if entry.count()==0:
				self.write_login_form("invalid Login",username,password)
			else:
				for ent in entry:
					if ent.password==valid_pw(username,password,ent.password):
						pa=str(ent.password)
						self.response.headers.add_header('Set-Cookie',"name=%s ; Path=/" % pa)
						un = str(hash_str(username)+'|'+username)
						
						self.response.headers.add_header('Set-Cookie', "u_name= % s ; Path = /" %un)
						self.redirect("/blog/welcome")
				else:
					error="invalid login"
					self.write_login_form(error,username,password)
					
		else:
			error="invalid login"
			self.write_login_form(error,username,password)

class Welcome(Handler):
	def get(self):
		password = self.request.cookies.get('u_name','')
		
		if password :
			password = password.split('|')[1]
			self.render("welcome.html",user=password)
		else:
			self.redirect("/blog/signup")
		


			
class Blog(Handler):
			
	def render_blog(self):
		username=self.request.cookies.get('u_name','')
		
		if username :
			username = username.split('|')[1]
			un = username
		else:
			un = None
		entry , age = get_post()

		tags , age = get_tags()
		self.render("bloghome.html",entry=entry,username=un,age=age,tags = tags)
	def get(self):
		self.render_blog()
		



class NewB_Entry(Handler):
	def render_newb(self,subject="",content="",error="",tag=""):
		self.render("newbentry.html",subject=subject,content=content,error=error,tag=tag)
		
	def get(self):
		password = self.request.cookies.get('u_name','')
		passHash = "am"
		if password == "" or password == None:
			self.redirect("/blog/login")
		else:
		  passHash = str(hash_str("amourphious")+'|'+"amourphious")
		  logging.error(passHash)
		
		if password == passHash:
			self.render_newb()
		else :
			self.render("404.html")
		
	def post(self):
		subject=self.request.get("subject")
		content=self.request.get("content")
		tag = self.request.get("tag")
		subtag =  self.request.get("subtag")
		
		password = self.request.cookies.get('u_name','')
		
		if password == "" or password == None :
			un = None
		else :
			password = password.split('|')[1]
			un = password
					
		if content and subject :
			a=Blog_Entry(subject=subject,content=content)
			if subtag :
				a.subtag = subtag
			if tag :
				a.tag = tag
			a_key=a.put()
			value , age = get_post(True)
			tag_lst = tag.split(";")
			logging.error(repr(tag_lst))
			ta =  db.GqlQuery("select * from Blog_tags")
			lst  = []
			for x in ta :
				lst.append(x.tag)
			for t in tag_lst :
				if t in lst :
					n = "a"
				else :
					tg = Blog_tags(tag = t)
					tg.put()
					get_tags(True)
			get_tags()
			get_post()
			self.redirect("/blog/%d"%a_key.id())
		else:
			error="please provide with valid title and content"
			self.render_newb(subject,content,error,tag)
			
class Logout(Handler):
	def get(self):
		self.response.headers.add_header("Set-Cookie","name=; Path=/")
		self.response.headers.add_header("Set-Cookie","u_name=; Path=/")
		self.redirect("/blog/signup")


class Permalink(Handler):

	def post(self,blog_id):
		posted_by=self.request.get("posted_by")
		user_email = self.request.get("user_email")
		comment=self.request.get("comment")
		if posted_by and comment and valid_email(user_email):
			a = Blog_comments(posted_by = posted_by ,comment = comment ,blog_id = blog_id, mail_id = user_email)
			a.put()
			get_comments(blog_id)
			r = db.GqlQuery("select * from Blog_comments where blog_id = '"+blog_id+"'")
			r = list(r)
			l = list();
			my_mail_id = "amourphious.appspot.com <amourphious1992@gmail.com>"
			sub = "New comment on Shivam's blog post"
			content = user_email + "commented on the Shivam's blog: \n" + comment + "\n visit: http://amourphious.appspot.com/blog/" + blog_id + "\n regards \n Amourphious"   
			for mid in r:
				if mid.mail_id  not in l:
					l.append(mid.mail_id)
					mail.send_mail(my_mail_id, mid.mail_id, sub, content)
			mail.send_mail(my_mail_id, user_email, sub, content)
			mail.send_mail("amourphious1992@gmail.com", "amourphious1992@gmail.com", sub, content)
			self.redirect("/blog/"+blog_id)
		else :
			self.render_permalink(blog_id,"Please enter Name, email and Comment correctly")



	def render_permalink(self,blog_id,error=""):
		comments , age_comm = get_comments(blog_id)
		#self.write("cached " +str(int(age_comm)) + " s ago")
		comment_list=[]
		for comm in comments:
			comment_list.append(comm.comment_hashed())

		password=self.request.cookies.get('u_name','')
		if password == "" or password == None:
			un = None
		else:
			password = password.split('|')[1]
			un = password

		tags , tage = get_tags()

		d = Blog_Entry.get_by_id(int(blog_id))

		if d:
			#self.write("queried " + str(int(age)) + " seconds ago")
			self.render("permalink.html", post = d, error = error, comments = comment_list,username = un , tags = tags)
		else :
			self.render("404.html")

	def get(self,blog_id):
		self.render_permalink(blog_id)


class Permalink_Jason(Handler):
	def get(self,blog_id):
		self.response.headers['Content-Type'] = "application/json; charset=utf-8"
		key = "POST" + blog_id
		
		s , age = get_key(key)
		
		if not s :
			d = Blog_Entry.get_by_id(int(blog_id))
			set_age(key , d)
			s , age = get_key(key)
		if s:
			content=s.content
			subject=s.subject
			created=s.created
			json_str=json.dumps({"content":content,"subject":subject,"created":created.strftime("%b %d, %Y")})
			self.write(json_str)
		else :
			self.render("404.html")
			
class Blog_json(Handler):
	def get(self):
		self.response.headers['Content-Type'] = "application/json; charset=utf-8"
		entry , age = get_post()
		json_lst=[]
		for ent in entry:
			content=ent.content
			subject=ent.subject
			created=ent.created
			json_str={"content":content,"subject":subject,"created":created.strftime("%b %d, %Y")}
			json_lst.append(json_str)
		json_output=json.dumps(json_lst)
		self.write(json_output)
			

class Ipu(Handler):
	def makexml(self):
		ipu_xml_str=Document()
		try:
			contents=urllib2.urlopen("http://www.ipu.ac.in/newmsg/latestmsg.htm").read()
		except:
			return
		if contents:
			table = ipu_xml_str.createElement("Tbl")
			ipu_xml_str.appendChild(table)
			link_table=split_htm(table_re,contents,"</table>")[1]
			row=split_htm(row_re,link_table,"</tr>")
			for r in row :
				row = ipu_xml_str.createElement("row")
				table.appendChild(row)
				column_lst=split_htm(column_re,r,"</td>")
				if len(column_lst)>3:
					if column_lst[2]:
						title = ipu_xml_str.createElement("title")
						row.appendChild(title)
						a=re.sub(tag_re,'',column_lst[2])
						a=re.sub(ecs_re,'',a)
						ptext = ipu_xml_str.createTextNode(a)
						title.appendChild(ptext)
					if column_lst[3]:
						match = re.search(r'href=[\'"]?([^\'" >]+)', column_lst[3])
						if match:
							a=match.group(0).replace('href="','')
							link = ipu_xml_str.createElement("link")
							row.appendChild(link)
							ptext = ipu_xml_str.createTextNode(a)
							link.appendChild(ptext)
					if column_lst[4]:
						date = ipu_xml_str.createElement("date")
						row.appendChild(date)
						ptext = ipu_xml_str.createTextNode(column_lst[4])
						date.appendChild(ptext)
		return ipu_xml_str
				
		
	def get(self):
		self.response.headers['Content-Type'] = "text/xml; charset=iso-8859-1"
		x=self.makexml()
		a=x.toprettyxml(indent="  ")
		self.write(a)
		

				



class Tag_page(Handler) :
	

	def get(self,pg_tag) :
		username=self.request.cookies.get('u_name','')
		if username :
			username = username.split('|')[1]
			un = username
		else:
			un = None
		entry , age = get_post()
		post = []
		for ent in entry :
			if pg_tag in ent.tag :
				table = {}
				table["subject"] = ent.subject
				table["content"] = ent.content
				table["created"]  = ent.created.strftime("%b %d, %Y")
				table["tag"] = ent.tag
				table["ide"] = ent.ide()
				post.append(table)
		tags , age = get_tags()
		lst = []
		for t in tags :
			lst.append(t.tag)
			
		if pg_tag in lst :
			self.render("tagpage.html" , entry = post , username=un , tg = pg_tag , tags = tags)
		else :
			self.write(repr(tags))
			
class Contact (Handler) :
	def get(self) :
		self.render("contact.html")
		

class PesrsonalDetails(Handler):
	
	def fetch_docs(self):
		docs = db.GqlQuery("select * from Documents")
		docs = list(docs)
		
		return docs
			
			
	def render_documents(self,title="",error=""):
		
		docs = self.fetch_docs()
		img_url=None
		self.render("Documents.html", error=error, title=title, docs = docs, img_url = img_url)
	
	def get(self):
		#self.write(repr(self.getlocation(self.request.remote_addr)))
		#self.write(repr(self.request.remote_addr))
		password = self.request.cookies.get('u_name','')
		passHash = "am"
		if password == "" or password == None:
			self.redirect("/blog/login")
		else:
		  passHash = str(hash_str("amourphious")+'|'+"amourphious")
		  logging.error(passHash)
		
		if password == passHash:
			self.render_documents()
		else :
			self.render("404.html")
		
	def post(self):
		title=self.request.get("title")
		doc = self.request.get("doc")
		doc = str(doc)
		
		if title :
			a=Documents(title=title)
			if doc :
				img = db.Blob(doc)
				image = Image(image = img)
				image.put()
				a.doc = str(image.img_key()) 
			
			a.put()
			
			get_troll_img(image.img_key() , True)
			
			self.fetch_docs()
			self.render_documents()
			self.redirect("/documents")
		else :
			error="Please provide with both doc and title"
			self.render_documents(title, error)


class car_meat_signup(Handler):
	def get(self):
		self.render("form_login_signup.html")
	
	def post(self):
		username=self.request.get("signup_user_name")
		password=self.request.get("signup_password")
		name = self.request.get("signup_name")
		car = self.request.get("signup_car")
		email = self.request.get("signup_email")
		user =  db.GqlQuery("select * from user where username ='" + username + "'")
		user = list(user)
		i = 0
		for us in user:
			i = i+1
			logging.error(us.username + " " + us.password)
		if(i == 0):
			hashed_password=make_pw_hash(username,password)
			new_user=user(username=username,password=hashed_password,name = name, car = car, email = email)
			a_key=new_user.put()
			self.response.headers.add_header('Set-Cookie',"name=%s ; Path=/" % str(hashed_password))
			self.redirect("/carmeat/welcome")
		else:
			self.render("form_login_signup.html", error = "user Exists !")
		
class car_meat_login(Handler):
	def get(self):
		self.render("form_login_signup.html")
	def post(self):
		username=self.request.get("login_user_name")
		password=self.request.get("login_password") 
		user =  db.GqlQuery("select * from user where username ='" + username + "'")
		user = list(user)
		i = 0
		for us in user:
			i = i+1
			logging.error(us.username + " " + us.password)
		if(i > 0):
			if(valid_login(username, password, str(user[0].password))):
				self.response.headers.add_header('Set-Cookie',"name=%s ; Path=/" % str(user[0].password))
				self.redirect("/carmeat/welcome")
			else:
				self.render("form_login_signup.html", error = "invalid credentials")
		else:
			self.render("form_login_signup.html", error = "invalid credentials no user")

class car_meat_welcome(Handler):
	def get(self):
		password = self.request.cookies.get('name','')
		user =  db.GqlQuery("select * from user where password ='" + password + "'")
		if(user):
			self.write("welcome" + str(user[0].username))
		else:
			self.redirect("/carmeat/login")

PAGE_RE = r'((?:[a-zA-Z0-9_-]+/?)*)'


app = webapp2.WSGIApplication([ ('/' , Intro),
								('/home', MainPage),
								('/asciichan' , AsciiArt),
								('/blog' , Blog),
								('/contact' , Contact),
								("/blog/new" , NewB_Entry),
								("/blog/([0-9]+)" , Permalink),
								("/blog/signup" , Signup),
								("/blog/welcome" , Welcome),
								("/blog/login" , Login),
								("/blog/logout" , Logout),
								("/blog/([0-9]+).json" , Permalink_Jason),
								("/blog/.json" , Blog_json),
								("/ipu/xml" , Ipu),
								("/blog/tag/"+PAGE_RE , Tag_page ),
								("/image" , Disp_img),
								("/documents", PesrsonalDetails),
								("/carmeat/login", car_meat_login),
								("/carmeat/signup", car_meat_signup),
								("/carmeat/welcome", car_meat_welcome)],
								 debug=True)

