#-*- coding: UTF-8 -*-

import os, win32com.client, unicodedata

def deAccent(str):
    return unicodedata.normalize('NFKD', str).encode('ascii','ignore')
    
def replace(string):
    replace_char = [" ",",","'","&","and"]
    for char in replace_char:
        string.replace(char,"-")
    return string

class Lyrics:
    def __init__( self ):
        self.song = Song()
        self.lyrics = ""
        self.source = ""

class Song:
    def __init__( self, artist="", title="", lyrics=None):
        self.artist = deAccent(artist)
        self.title = deAccent(title)
        self.lyrics = lyrics

    def __str__(self):
        return "Artist: %s, Title: %s" % ( self.artist, self.title)

    def __cmp__(self, song):
        if (self.artist != song.artist):
            return cmp(self.artist, song.artist)
        else:
            return cmp(self.title, song.title)

    def sanitize(self, str):
        return str.replace( "\\", "_" ).replace( "/", "_" ).replace(":","_").replace("?","_").replace("!","_")

    def path(self):
        return unicode( os.path.join( __profile__, "lyrics", self.sanitize(self.artist), self.sanitize(self.title) + ".txt" ), "utf-8" )

scrapers = []
LYRIC_SCRAPER_DIR = os.getcwd() + os.sep + "scrapers"
for scraper in os.listdir(LYRIC_SCRAPER_DIR):
    if os.path.isdir(os.path.join(LYRIC_SCRAPER_DIR, scraper)) and ("__init__" not in scraper):
        print "Loading scaper: ", scraper
        exec ( "from scrapers.%s import lyricsScraper as lyricsScraper_%s" % (scraper, scraper))
        exec ( "scrapers.append(lyricsScraper_%s.LyricsFetcher())" % scraper)


def GetLyrics(song):
    for scraper in scrapers:
        try:
            lyrics, error, service = scraper.get_lyrics_thread( song )
        except Exception, e:
            lyrics = None
            pass
        if lyrics is not None:
            ##log('%s: found lyrics' % service)
            break
        else:
            continue
            ##log('%s: no results found' % service)
    song.lyrics = lyrics

def main():
    it = win32com.client.Dispatch("iTunes.Application")
    tracks = it.LibraryPlaylist.Tracks
    notadded = []
    added = []
    haslyr = []
    icloudonly = []
    for track in tracks:
        try:
            #print "----------------"
            #print track.Name
            #print track.Artist
            #print track.Album
            trackex = win32com.client.CastTo(track,'IITFileOrCDTrack')
            if (trackex.Lyrics == ""):
                song = Song(track.Artist, track.Name)
                GetLyrics(song)
                trackex.Lyrics = song.lyrics
                added.append(track.Name)
                continue
            else:
                haslyr.append(track.Name)
                continue
            notadded.append(track.Name)
            del trackex
        except Exception, e:
            try:
                icloudonly.append(track.Name)
                #print "EXCEPTION: " + track.Name
            except:
                #print "EXCEPTION: Unknown Song"
                pass
            #print e
            continue
            pass
    stats = open("stats.txt", "a")
    import time
    stats.write("\r\n-------------------")
    stats.write(time.asctime())
    stats.write("-------------------\r\n")
    stats.write("Total Songs in Library: " + str(len(added) + len(notadded) + len(icloudonly)+len(haslyr)) + "\r\n")
    stats.write("Songs that already had lyrics: " + str(len(haslyr)) + "\r\n")
    stats.write("Songs that were not included (iCloud or missing files): " +  str(len(icloudonly)) +"\r\n")
    stats.write("Songs that had lyrics added: "+ str(len(added))+"\r\n")
    stats.write("Songs for which no lyrics were found online: "+ str(len(notadded))+"\r\n")
    stats.close()
    
            
if __name__ == '__main__':
    main()