#-*- coding: UTF-8 -*-
import sys, re, urllib2, socket, HTMLParser
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

__service__ = 'lyricwiki'

socket.setdefaulttimeout(10)

class LyricsFetcher:
    def __init__( self ):
        self.url = 'http://lyrics.wikia.com/api.php?artist=%s&song=%s&fmt=realjson'

    def get_lyrics_thread(self, song):
        #log( "%s: searching lyrics for %s" % (__service__, song))
        #log( "%s: search api url: %s" % (__service__, self.url))
        a = self.url % (urllib2.quote(song.artist), urllib2.quote(song.title))
        req = urllib2.urlopen(self.url % (urllib2.quote(song.artist), urllib2.quote(song.title)))
        response = req.read()
        req.close()
        data = simplejson.loads(response)
        try:
            self.page = data['url']
        except Exception, e:
            return None, None, __service__
        if not self.page.endswith('action=edit'):
            #log( "%s: search url: %s" % (__service__, self.page))
            req = urllib2.urlopen(self.page)
            response = req.read()
            req.close()
            matchcode = re.search('lyricbox.*?div>(.*?)<!--', response)
            try:
                lyricscode = (matchcode.group(1))
                htmlparser = HTMLParser.HTMLParser()
                lyr = htmlparser.unescape(lyricscode).replace('<br />', '\n')
                return lyr, None, __service__
            except Exception, e:
                return None, None, __service__
        else:
            return None, None, __service__
