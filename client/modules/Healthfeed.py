import feedparser
import app_utils
import re
from semantic.numbers import NumberService
import sys
from random import randint

#usage:
# Command:  Health


WORDS = ["HEALTH", "NEWS", "FIRST", "SECOND", "THIRD", "FOURTH"]

URL = 'http://www.medicinenet.com/rss/general/womens_health.xml'

MAXNEWS = 5

class Report:

    def __init__(self, link, description):
        self.link = link
        self.description = description


def getReports():
    d = feedparser.parse(URL)
    count = 0
    reports = []
    for item in d['items']:
        reports.append(Report(item['link'],item['title']))
    return reports


def handle(text, mic, profile):
#def handle(text):
    """
        
        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone number)
    """
    mic.say("Pulling up the health news")
    # print("pulling up the health news")
    reports = ""
    COUNT = MAXNEWS
    healthreports = getReports()
    copyreports = healthreports
    # test to ensure the MAXNEWS is less then the number of healthreports
    if MAXNEWS >= len(healthreports):
	COUNT = healthreports
    # randomly choice four news reports
    for r in range(0,MAXNEWS):
	x = randint(0,len(copyreports)-1)
        reports = reports + str(r+1) + ")... " + copyreports[x].description + " ... "
        #remove the report from the list so we don't randomly choose two devices
        copyreports.pop(x)
 
    def handleResponse(text):

        def extractOrdinals(text):
            output = []
            service = NumberService()
            # convert to lower case for the ordinal function
            text = text.lower()
            for w in text.split():
 		#print (w + "inside extract Ordinals")
                if w in service.__ordinals__:
		    print(w + " is a n ordinal")
                    output.append(service.__ordinals__[w])
            return [service.parse(w) for w in output]

        chosen_articles = extractOrdinals(text)
        send_all = chosen_articles == [] and app_utils.isPositive(text)

        if send_all or chosen_articles:
            mic.say("Sure, just give me a moment")

            if profile['prefers_email']:
                body = "<ul>"

            def formatArticle(article):
                tiny_url = app_utils.generateTinyURL(article.link)

                if profile['prefers_email']:
                    return "<li><a href=\'%s\'>%s</a></li>" % (tiny_url,
                                                               article.description)
                else:
                    return article.description + " -- " + tiny_url

            for idx, article in enumerate(healthreports):
                if send_all or (idx + 1) in chosen_articles:
                    article_link = formatArticle(article)

                    if profile['prefers_email']:
                        body += article_link
                    else:
                        if not app_utils.emailUser(profile, SUBJECT="", BODY=article_link):
                            mic.say(
                                "I'm having trouble sending you these articles. Please make sure that your phone number and carrier are correct on the dashboard.")
                            return

            # if prefers email, we send once, at the end
            if profile['prefers_email']:
                body += "</ul>"
                if not app_utils.emailUser(profile, SUBJECT="From the Front Page of Health News", BODY=body):
                    mic.say(
                        "I'm having trouble sending you these articles. Please make sure that your phone number and carrier are correct on the dashboard.")
                    return

            mic.say("All done.")

        else:
            mic.say("OK I will not send any articles")

    if profile['phone_number']:
        mic.say("Here are some front-page health articles. " +
                reports + ". Would you like me to send you these? If so, which?")
        handleResponse(mic.activeListen())

    else:
        mic.say(
            "Here are some front-page articles. " + reports)


def isValid(text):
    """
        Returns True if the input is related to the news.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\b(health)\b', text, re.IGNORECASE))


#healthnews = handle("this is a test")
#print(isValid("health"))
