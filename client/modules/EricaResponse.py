import re
import sys
import random

PRIORITY = 6

WORDS = ["HELLO", "QUIET", "SHUT"]

def handle(text, mic, profile):
#def handle(text):
    
 
    if bool(re.search(r'\b(hello)\b', text, re.IGNORECASE)):
       sayings= ['Hello there ','What a good day','Take Care', 'sweet', 'What is up', 'cool', 'Be happy', 'Say Erica and I will listen to command']
       styleSaying = random.choice(sayings)
       mic.say(styleSaying)
    
    if bool(re.search(r'\b(be quiet)\b', text, re.IGNORECASE)):
       sayings= ['OK, I will try to be quiet', 'I do not think so', 'So,    Maybe I will or maybe I will not']
       styleSaying = random.choice(sayings)
       mic.say(styleSaying)


    if bool(re.search(r'\b(shut up)\b', text, re.IGNORECASE)):
       sayings= ['Please do not use     that voice with me',  ' Is that voice honorable?', 'your statement is now recorded for playback to Mom and Dad.   Please do not use that again' ]
       styleSaying = random.choice(sayings)
       mic.say(styleSaying)


def isValid(text):
    """
        Returns True if the input is related to the news.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\b(hello|be quiet|shut up)\b', text, re.IGNORECASE))


