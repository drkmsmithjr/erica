import feedparser
import app_utils
import re
from semantic.numbers import NumberService
import sys
from random import randint

#usage:
# Command:  repeat    . Erica will ask for phrase to repeat.   Save this to repeat.wav
# Command:  again.  Erica will play the phrase again.


WORDS = ["REPEAT", "AGAIN"]


def handle(text, mic, profile):
#def handle(text):
    """
        
        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone number)
    """


    print("testing for Repeat")
    def handleResponse(text):

        mic.say(text)
        repeat_phrase = open("repeat.txt","w")
        repeat_phrase.seek(0,0)
        repeat_phrase.write(text)
        repeat_phrase.close()
        

# test if repeat agian was seen or just repeat
    if bool(re.search(r'\b(again)\b', text, re.IGNORECASE)):
        try:
            repeat_phrase = open("repeat.txt","r")
            a = repeat_phrase.read()
            mic.say(a)
            repeat_phrase.close()
        except:
            mic.say("I didn't recognize have anything to repeat")
    else:
        mic.say("At the promt, say the phrase you want me to remember")
        handleResponse(mic.activeListen())
                

def isValid(text):
    """
        Returns True if the input is related to the news.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\b(repeat|again)\b', text, re.IGNORECASE))


#healthnews = handle("this is a test")
#print(isValid("health"))
