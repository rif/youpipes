import cgi
import os
import webapp2
import jinja2

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

  def post(self):
    search_term = cgi.escape(self.request.get('content')).encode('UTF-8')
    if not search_term:
        self.redirect('/')
        return

    client = gdata.youtube.service.YouTubeService()
    gdata.alt.appengine.run_on_appengine(client)
    query = gdata.youtube.service.YouTubeVideoQuery()

    query.vq = search_term
    query.max_results = '5'
    template_values = {
        'feed': client.YouTubeQuery(query),
        'search_term': search_term,
    }
    template = jinja_environment.get_template('templates/search.html')
    self.response.out.write(template.render(template_values))

           
app = webapp2.WSGIApplication([('/', MainPage)],debug=True)
