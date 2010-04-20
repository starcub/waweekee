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
import re, string

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
	
class Ngram(webapp.RequestHandler):
    def post(self):
        text = cgi.escape(self.request.get('content1'))
        gram1 = text.split()
        gram2=[]
        gram3=[]
        gram4=[]
        for i in range(0,len(gram1)-1):
            gram2.append(gram1[i] + ' ' + gram1[i+1])
        for i in range(0,len(gram1)-2):
            gram3.append(gram1[i] + ' ' + gram1[i+1] + ' ' + gram1[i+2])
        for i in range(0,len(gram1)-3):
            gram4.append(gram1[i] + ' ' + gram1[i+1] + ' ' + gram1[i+2] + ' ' + gram1[i+3])
        self.response.out.write('<html><body>')
        self.response.out.write('<h1>Unstripped</h1>')
        self.response.out.write('unigram:<pre>')
        self.response.out.write(gram1)
        self.response.out.write('</pre>')
        self.response.out.write('bigram:<pre>')
        self.response.out.write(gram2)
        self.response.out.write('</pre>')
        self.response.out.write('trigram:<pre>')
        self.response.out.write(gram3)
        self.response.out.write('</pre>')
        self.response.out.write('quadgram:<pre>')
        self.response.out.write(gram4)
        self.response.out.write('</pre>')
        self.response.out.write('<h1>Stripped</h1>')
        self.response.out.write('unigram:<pre>')
        self.response.out.write(self.stripStopwords(self.stripPunctuation(gram1)))
        self.response.out.write('</pre>')
        self.response.out.write('bigram:<pre>')
        self.response.out.write(self.stripStopwords(self.stripPunctuation(gram2)))
        self.response.out.write('</pre>')
        self.response.out.write('trigram:<pre>')
        self.response.out.write(self.stripStopwords(self.stripPunctuation(gram3)))
        self.response.out.write('</pre>')
        self.response.out.write('quadgram:<pre>')
        self.response.out.write(self.stripStopwords(self.stripPunctuation(gram4)))
        self.response.out.write('</pre>')
        self.response.out.write('</pre></body></html>')
        
    def stripPunctuation(self, word_list):
        punctuation = re.compile(r'[.?!,":;]')
        punctuation = re.compile('[%s]' % re.escape(string.punctuation))
        #
        wl2 = []
        for word in word_list:
        #
        # remove punctuation marks
        #
            word2 = punctuation.sub("", word)
            wl2.append(word2)
        return wl2
    def stripStopwords(self, word_list):
        stopwords = ["a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone", "along", "already", "also","although","always","am","among", "amongst", "amoungst", "amount",  "an", "and", "another", "any","anyhow","anyone","anything","anyway", "anywhere", "are", "around", "as",  "at", "back","be","became", "because","become","becomes", "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides", "between", "beyond", "bill", "both", "bottom","but", "by", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down", "due", "during", "each", "eg", "eight", "either", "eleven","else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own","part", "per", "perhaps", "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious", "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thickv", "thin", "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves", "the"]
        index=0
        while index < len(word_list):
            word = word_list[index]
            if len(word.split()) < 2:
                if word.split()[0].lower() in stopwords:
                    word_list.remove(word_list[index])
                else:
                    index= index+1
                continue
            else:
                if word.split()[0].lower() in stopwords or word.split()[len(word.split())-1].lower() in stopwords:
                    word_list.remove(word_list[index])
                else:
                    index= index+1
        return word_list
        
application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/wikify', Wikify),
									  ('/ngram', Ngram)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()