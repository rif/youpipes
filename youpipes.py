import cgi
import os
import webapp2
import jinja2
import datetime
from google.appengine.api import mail
from google.appengine.api import memcache

import gdata.youtube
import gdata.youtube.service
import gdata.alt.appengine

jinja_environment = jinja2.Environment(extensions=['jinja2.ext.autoescape'],
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__))) 

class MainPage(webapp2.RequestHandler):
  def get(self):   
    if self.request.host == 'youpipes.appspot.com':     
        self.redirect('http://youhe.ro')
    front_page = memcache.get('front_page')
    if front_page is None:            
        client = gdata.youtube.service.YouTubeService()
        gdata.alt.appengine.run_on_appengine(client)    
        template_values = {
            'feed': client.GetRecentlyFeaturedVideoFeed(),
            'title': 'Recently Featured Videos',
            'autoplay': 'false',
            }
        template = jinja_environment.get_template('templates/index.html')
        front_page = template.render(template_values)
        memcache.set('front_page', front_page, 60 * 60) #cache for one hour
    self.response.out.write(front_page)

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
    query.max_results = self.request.cookies.get('items_per_page', '25')
    template_values = {
        'feed': client.YouTubeQuery(query),
        'title': "Searching for '%s'" % search_term.decode('UTF-8'),
        'autoplay': 'true',
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
        message = mail.EmailMessage(sender="Radu Fericean (YouHero) <fericean@gmail.com>",
                            subject="YouHero message from %s (%s)" % (name, email))
        message.to = "Radu Fericean <radu@fericean.ro>"
        message.body = cgi.escape(self.request.get('content'))
        message.send()
        self.redirect('/')

class AboutPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/about.html')
        self.response.out.write(template.render({})) 

class ItemsPerPageQuery(webapp2.RequestHandler):
    def get(self):
        expiration = datetime.datetime.utcnow() + datetime.timedelta(days=30)
        self.response.headers.add_header('Set-Cookie','items_per_page=%s; expires=%s; path=/search;' %
            (str(self.request.get("nb", '25')), expiration.strftime("%a, %d-%b-%Y %H:%M:%S UTC")))
    
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/search', SearchPage),
    ('/about', AboutPage),
    ('/contact', ContactPage),
    ('/items', ItemsPerPageQuery),    
    ],debug=True)
