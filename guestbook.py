import cgi
import urllib
import os

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

#Set a parent key on Greetings , ensure they are all in the same entity group
#Remember: queries across the single entity group will be more consistent

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
	"""Constructs a Datastore key for a Guestbook entity with guestbook_name."""
	return ndb.Key('Guestbook', guestbook_name)

class Greeting(ndb.Model):
	"""Models an individual Guestbook entry with author, content, and date."""
	author = ndb.UserProperty()
	content = ndb.StringProperty(indexed=False)
	date = ndb.DateTimeProperty(auto_now_add=True)

class MainPage(webapp2.RequestHandler):

    def get(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
 
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        
        greetings = greetings_query.fetch(10)

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'greetings': greetings,
            'guestbook_name': guestbook_name,
            #urllib.urlencode({'guestbook_name': guestbook_name}),
            #'guestbook_name': urllib.urlencode(guestbook_name),
            'url': url,
            'url_linktext': url_linktext,
        }

    	template = JINJA_ENVIRONMENT.get_template('index.html')    	
    	self.response.write(template.render(template_values))

#we set the same parent key on the 'Greeting' , to ensure that each greeting is in the same entity group
# thus queries across the single entity group will be consistent

class Guestbook(webapp2.RequestHandler):
	def post(self):
		guestbook_name = self.request.get('guestbook_name',
											DEFAULT_GUESTBOOK_NAME)
		greeting = Greeting(parent=guestbook_key(guestbook_name))

		if users.get_current_user():
			greeting.author = users.get_current_user()

		greeting.content = self.request.get('content')
		greeting.put()

		query_params = {'guestbook_name':guestbook_name}
		print 'DEBUG::: '+str(query_params)
		# the redirect is for the guest book page where we are posting to
		self.redirect('/?'+urllib.urlencode(query_params))

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
], debug=True)