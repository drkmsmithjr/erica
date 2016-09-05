import feedparser
import app_utils
import re
from semantic.numbers import NumberService
import sys

#usage:
# Command:  SURF REPORT
# Default Breaks:
#   1. Salt Creek
#   2. Doheny
#   3. Upper Trestles


WORDS = ["SURF", "REPORT", "SPOT"]

URL= [0,1,2,3,4]
URL[0]= 'http://feeds.feedburner.com/surfline-rss-surf-report-south-orange-county'
URL[1]= 'http://feeds.feedburner.com/surfline-rss-surf-report-north-orange-county'
URL[2]= 'http://feeds.feedburner.com/surfline-rss-surf-report-north-san-diego'
URL[3]= 'http://feeds.feedburner.com/surfline-rss-surf-report-south-san-diego'
URL[4]= 'http://feeds.feedburner.com/surfline-rss-surf-report-san-luis-obispo-county'

SURFSPOTS= ['SALT CREEK','DOHENY','UPPER TRESTLES']


class SurfReport:

    def __init__(self, spot, report):
        self.spot = spot
        self.report = report


def getSurfReports(specific=None):
    d = feedparser.parse(URL[0])
    count = 0
    reports = []
    if specific == None:
        for item in d['items']:
            for spot in SURFSPOTS:
                if item['title'].find(spot) != -1:
#                    reports.append(item['title'])
                     reports.append(SurfReport(spot,item['title']))
    else:
        for URLx in URL:
            d = feedparser.parse(URLx)
            for item in d['items']:
                 if item['title'].find(specific.upper()) != -1:
#                     reports.append(item['title'])
                      reports.append(SurfReport(specific.upper(),item['title']))
		      return reports
    return reports


def handle(text, mic, profile):
#def handle(text):
    """
        Responds to user-input, typically speech text, with a summary of
        the surf report for Salt Creek, Deheany, and Upper Tresles
        
        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone number)
    """
    mic.say("Pulling up the surf reports")
    if bool(re.search(r'\b(report for)\b', text, re.IGNORECASE)):
       n = re.search(r'\b(for [a-z]+)\b', text, re.IGNORECASE)
       print(n)
       if bool(n):
          specificSpot = n.group(0).split()[1]
       else:
          specificSpot = None
    else:
       specificSpot = None
    reports = "Here are the current surf Conditions. "
    surfreports = getSurfReports(specificSpot)
    print("after getting the surf reports")
    print(surfreports)
    if len(surfreports) > 0:
       for r in surfreports:
          reports = reports + "The report for " + r.report + " . "
    else:
       reports = "I could not find the report for " + specificSpot + " . "  
    mic.say(reports)
    print(reports)




def isValid(text):
    """
        Returns True if the input is related to the news.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\b(surf)\b', text, re.IGNORECASE))


#handle("this is a test")
#print(isValid("report"))
