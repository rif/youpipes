import cgi
import os
import webapp2
import jinja2
from google.appengine.api import mail

import gdata.youtube
import gdata.youtube.service
import gdata.alt.appengine

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__))) 

class MainPage(webapp2.RequestHandler):
  def get(self):    
    client = gdata.youtube.service.YouTubeService()
    gdata.alt.appengine.run_on_appengine(client)    
    template_values = {'feed': client.GetRecentlyFeaturedVideoFeed()}
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
        'search_term': search_term,
    }
    template = jinja_environment.get_template('templates/search.html')
    self.response.out.write(template.render(template_values))

class ContactPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/contact.html')
        self.response.out.write(template.render({}))        
    def post(self):
        message = mail.EmailMessage(sender="Radu Fericean (YouPipes) <fericean@gmail.com>",
                            subject="YouPipes message from " + cgi.escape(self.request.get('email')))
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
