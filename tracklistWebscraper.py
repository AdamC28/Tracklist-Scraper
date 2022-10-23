from bs4 import BeautifulSoup
import requests
from requests_html import HTMLSession
from urllib.parse import urlparse

'''
primary scrape for soundcloud releases.
grabs useful data and passes it directly for track scraping.
if a multitrack release is given, it has to dynamically scrape,
repeating the process with an html session
'''

def scInitScrape(url):
    #gets source html from url
    source = requests.get(url).text
    #makes workable BeautifulSoup object
    soup = BeautifulSoup(source, "html.parser")
    #second noscript tag has all useful data on soundcloud
    nScript = soup.body.find_all('noscript')[1].article
    #soundcloud classifies release types by "schema"
    schema = nScript['itemtype']

    #albums/eps and playlists can be scraped the same way
    if schema == 'http://schema.org/MusicAlbum' or schema == 'http://schema.org/MusicPlaylist':
        albumSessionScrape(url)
    #for individual tracks
    elif schema == 'http://schema.org/MusicRecording':
        trackScrape(nScript, 1)
    #invalid release type
    else:
        print("Invalid release type! (Not an album, playlist, or track)")

'''
creates a dynamic session to scrape a multitrack release
loads in every track, then gets its useful data and sends for direct track scraping
'''
def albumSessionScrape(url):
    #open HTML session to scrape dynamically loaded tracklist
    session = HTMLSession()
    r = session.get(url)

    #scroll down to load (most) tracklists in full
    r.html.render(scrolldown=10, sleep=1, keep_page=True)

    #extract every track item in rendered tracklist
    tracklist = r.html.find('li.trackList__item')

    #used in trackScrape() output to identify track number
    trackCount = 1
    
    for track in tracklist:
        #extract hyperlink for track, which is contained in a set
        trackSet = track.find('a.trackItem__trackTitle')[0]
        
        #access only element of set (the link necessary to scrape)
        trackUrl = next(iter(trackSet.absolute_links))

        #gets html code of song from source urls
        source = requests.get(trackUrl).text
        #makes workable BeautifulSoup object from source
        soup = BeautifulSoup(source, "html.parser")
        #represents noscript tag containing all useful data
        nScript = soup.body.find_all('noscript')[1].article

        trackScrape(nScript, trackCount)
        trackCount += 1

'''
does all the actual scraping for any given release
an individual track's noscript tag is given, data manually parsed
the second print() statement oututs in RateYourMusic's recognized tracklist format.
the other format is left over from testing
'''
def trackScrape(nScript, trackNum):
    #track and artist name are contained in hyperlinks
    links = nScript.header.h1.find_all('a')

    #grabs slice of song duration from specific meta tag
    duration = nScript.find_all('meta')[0]["content"][2:]
    trackLength = duration[3:5] + ":" + duration[6:8] #takes only min, second values

    if duration[:2] != '00':
        trackLength = duration[:2] + ":" + trackLength #takes hour if >= 1

    trackName = links[0].text
    artistName = links[1].text
    
    #retrieves release date from formatted time tag
    pubdate = (nScript.time.text).split('T')[0]

    #print(f"{artistName} - {trackName}|{trackLength} ({pubdate})")
    print(f"{trackNum}|{trackName}|{trackLength}")

'''
specifically for scraping tracklists from NTS Live mixes
returns the results in an easy-to-paste RateYourMusic format
'''
def ntsSessionScrape(url):
    session = HTMLSession()
    r = session.get(url)

    r.html.render(sleep=1, keep_page=True)

    tracks = r.html.find('li.track')
    trackCount = 1

    for track in tracks:
        print(f"{trackCount}|{track.find('span.track__artist')[0].text} - {track.find('span.track__title')[0].text}|")
        trackCount += 1

#runtime starts here, takes basic user input in the form of a URL
link = input("Enter URL:\n")
#grabs website (host) name
domain = urlparse(link).netloc

#identify website and use appropriate scraping
if domain == 'soundcloud.com':
    scInitScrape(link)
elif domain == 'www.nts.live':
    ntsSessionScrape(link)