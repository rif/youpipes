import cgi
import os
import webapp2
import jinja2
from google.appengine.api import mail

import gdata.youtube
import gdata.youtube.service
import gdata.alt.appengine

jinja_environment = jinja2.Environment(extensions=['jinja2.ext.autoescape'],\
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__))) 

class MainPage(webapp2.RequestHandler):
  def get(self):    
    client = gdata.youtube.service.YouTubeService()
    gdata.alt.appengine.run_on_appengine(client)    
    template_values = {
        'feed': client.GetRecentlyFeaturedVideoFeed(),
        'title': 'Recently Featured Videos'
        }
    template = jinja_environment.get_template('templates/index.html')
    self.response.out.write(template.render(template_values))

class SearchPage(webapp2.RequestHandler):
  def get(self):
    search_term = cgi.escape(self.request.get("v")).encode('UTF-8')    

    if not search_term:
        self.redirect('/')
        return

    client = gdata.youtube.service.YouTubeService()
    gdata.alt.appengine.run_on_appengine(client)
    query = gdata.youtube.service.YouTubeVideoQuery()

    query.vq = search_term
    query.max_results = '25'
    template_values = {
        'feed': client.YouTubeQuery(query),
        'title': "Searching for '%s'" % search_term,
        'search_term': search_term,
    }
    template = jinja_environment.get_template('templates/index.html')
    self.response.out.write(template.render(template_values))

class ContactPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/contact.html')
        self.response.out.write(template.render({}))        
    def post(self):
        name = cgi.escape(self.request.get('from')).encode('UTF-8')
        email = cgi.escape(self.request.get('email')).encode('UTF-8')
        message = mail.EmailMessage(sender="Radu Fericean (YouPipes) <fericean@gmail.com>",
                            subject="YouPipes message from %s (%s)" % (name, email))
        message.to = "Radu Fericean <radu@fericean.ro>"
        message.body = cgi.escape(self.request.get('content'))
        message.send()
        self.redirect('/')
        

class AboutPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/about.html')
        self.response.out.write(template.render({})) 
           
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/search', SearchPage),
    ('/about', AboutPage),
    ('/contact', ContactPage),
    ],debug=True)
