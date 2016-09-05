from notifier import Notifier
from musicmode import *
from brain import Brain
from modules import *
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")


# Needs to be BCM. GPIO.BOARD lets you address GPIO ports by periperal
# connector pin number, and the LED GPIO isn't on the connector
#GPIO.setmode(GPIO.BCM)

# set up GPIO output channel
#GPIO.setup(16, GPIO.OUT)



class Conversation(object):

    def __init__(self, persona, mic, profile):
        self.persona = persona
        self.mic = mic
        self.profile = profile
        self.brain = Brain(mic, profile)
        self.notifier = Notifier(profile)

    def delegateInput(self, text, FoundPersona = True):
        """A wrapper for querying brain."""


        if FoundPersona:

           # check if input is meant to start the music module
           if any(x in text.upper() for x in ["SPOTIFY","MUSIC"]):
               self.mic.say("Please give me a moment, I'm loading your Spotify playlists.")
               music_mode = MusicMode(self.persona, self.mic)
               music_mode.handleForever()
               return

           # Timer module needs to have the notifier instance.
           # so this module has a different format that the normal ones.
           # The notifier module will also check more quickly for a timer event.
           # this will ensure that timer events occur inline with normal program flow
           # and will call the timer module first
           # Timer.isValid (text) 
           # Timer.handle(text, self.mic, self.profile, self.notifier):
           #      the handle will now be able to call function in notifier to push on queue.
           print("testing if timer is valid")	
	   if Timer.isValid(text):
	       print("timer is valid")
               try:
                  Timer.handle(text, self.mic, self.profile, self.notifier)
                  return
               except:
                  self.mic.say("I'm sorry. I had some trouble with the timer module. Please try again later.")
                  return
 
           # Query the brain to check if other modules are ok.
           self.brain.query(text)

        else:
           self.brain.passivequery(text)
    def handleForever(self):
        """Delegates user input to the handling function when activated."""
        while True:

            # Announce notifications until empty
            notifications = self.notifier.getAllNotifications()
            for notif in notifications:
		self.mic.say(notif)
#               print notif

	    # GPIO On
#	    GPIO.output(16, GPIO.LOW)
            try:
                threshold, transcribed = self.mic.passiveListen(self.persona)
            except:
                continue
	    # Off
#	    GPIO.output(16, GPIO.HIGH)	    

            # If threshold is false and transcribed value is a string.  
            # then I should look at values 
            if not threshold:
                if isinstance(transcribed,list):
                    if len(transcribed) == 2:
                       self.delegateInput(transcribed[0],False)
                       print(transcribed[0],' we did not detect erica')

            print ("in Handleforever")

            if threshold:
                input = self.mic.activeListen(threshold)
                print(input)
                if input:
                    self.delegateInput(input)
                else:
                    self.mic.say("Pardon?.  I did not recognize that command.  try to say it louder")
