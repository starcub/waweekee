#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import cgi
import urllib2
import os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.runtime import DeadlineExceededError


from xml.dom import minidom

class MainPage(webapp.RequestHandler):
  def get(self):
    template_values = {
      
    }
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))


class Wikify(webapp.RequestHandler):
  def post(self):
    contentText = self.request.get('content')
    text = self.request.get('splitContent').replace('%20',' ')
    wikifiedText = ''
    words = text.split()
    words = set(words)
    wikiAPI = "http://en.wikipedia.org/w/api.php?action=opensearch&search=%s&format=xml"
    response = text
    # firstly check if there is the wikipedia word, if so, wikify the word. this is importnat as otherwise it will mix up with the url later in the replace function.
    #response = response.replace('wikipedia', '<a href=\"http://en.wikipedia.org/wiki/Wikipedia/\" target=\"_blank\">wikipedia</a>')
    #response = response.replace('Wikipedia', '<a href=\"http://en.wikipedia.org/wiki/Wikipedia/\" target=\"_blank\">Wikipedia</a>')  
    try:
      isFirstTime = True
      for pos1, word in enumerate(words):
        sock = urllib2.urlopen(wikiAPI % word)
        data = sock.read()
        sock.close()
        xmldoc = minidom.parseString(data)
        if len(xmldoc.getElementsByTagName('Text')) > 0:
          for pos, item in enumerate(xmldoc.getElementsByTagName('Text')):
            if item.childNodes[0].nodeValue.lower() == word.lower():
              if isFirstTime == True:
                response = contentText.replace(word, '<a class=\"wikiLink\" href=\"%s\" target=\"_blank\">%s<span class=\"tip_info\">%s</span></a>' % (xmldoc.getElementsByTagName('Url')[pos].childNodes[0].nodeValue, word, xmldoc.getElementsByTagName('Description')[pos].childNodes[0].nodeValue))   
                isFirstTime = False
              else:
                response = response.replace(word, '<a class=\"wikiLink\" href=\"%s\" target=\"_blank\">%s<span class=\"tip_info\">%s</span></a>' % (xmldoc.getElementsByTagName('Url')[pos].childNodes[0].nodeValue, word, xmldoc.getElementsByTagName('Description')[pos].childNodes[0].nodeValue))
              break
      template_values = {
        'wikifiedText': wikifiedText,
      }
      self.response.out.write(response)
    except DeadlineExceededError:
      self.response.clear()
      self.response.set_status(500)
      self.response.out.write("Sorry but the operation has timed out... Timeout is currently set to 30s.")     
    
  def wikifying(self,text):
    wikifiedText = text.split()

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/wikify', Wikify)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()