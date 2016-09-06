import feedparser
import app_utils
import re
#from apscheduler.scheduler import Scheduler
from apscheduler.schedulers.background import BackgroundScheduler
import sys
import string


WORDS = ["TIMER", "SET", "FOR", "MINUTES"]

# set up the the timer 
#sched = Scheduler()
sched = BackgroundScheduler()
sched.start()



def settimer_job(name, notifier):
    notifier.timerDone(name)
    print("timer done")
    # name: string:  used to tell what timer in completed.
    # duration: int: use to tell the duration 
    # unit:  string:  either "seconds" , "minutes", "hours", days"
    # notifier:  Class notifier:   for adding to the notifier queue for reporting
    # Add the notifier to the cue
    


def handle(text, mic, profile, notifier):
#def handle(text):
    """
        
        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone number)
	notifier -- knows how to get to the notifier queue


    Voice commands:

       set timer:   set timer to days, hours, minutes, and seconds
       What timers are running:   Will list the timers and when they will be complete
       remove timer:  Will list the timers and ask which one to remove.
       what timer finished:  keep track of type and whoat timer finished.  


    """
    def handleResponse(text):
	return
# look for the a name after the FOR command
    print("testing for")
    if bool(re.search(r'\b(set)\b', text, re.IGNORECASE)):
         print("we found the set timer strings")
	 m = re.findall(r'\b(\d+ hours?|\d+ minutes?|\d+ days?|\d+ seconds?)\b', text, re.IGNORECASE)
	 if len(m) > 0:
             Duration = []
	     TimerUnit = []	 
             for a in m:
	        #At least one match was found  
	        a = a.split()
                #Add an S to the end of the Hour,minute, days, second if needed
	        a[1] = a[1].upper()
                if a[1][len(a[1])-1] != 'S':
                   a[1] = a[1] + 'S'
	        Duration.append(a[0])
	        TimerUnit.append(a[1])
             n = re.search(r'\b(for [a-z]+)\b', text, re.IGNORECASE)
             if bool(n):
	         TimerName = n.group(0).split()[1]
	     else:
                 TimerName = ""
             saystr = "The " + TimerName + " timer will be set for "
             if TimerName == "":
                 TimerName = "BASIC"
             for x in range(len(m)):	         	
                 saystr = saystr + Duration[x] + " " + TimerUnit[x] + " "
             mic.say(saystr)

             # set the timer 
#             sched = Scheduler()
#             sched.start()
             Days = 0
             Hours = 0
             Minutes = 0
             Seconds = 0
	     # determine if Days, hours, minutes, or seconds were used
             if 'DAYS' in TimerUnit:
 	        Days = int(Duration[TimerUnit.index('DAYS')])
             if 'HOURS' in TimerUnit:
 	        Hours = int(Duration[TimerUnit.index('HOURS')])
             if 'MINUTES' in TimerUnit:
 	        Minutes = int(Duration[TimerUnit.index('MINUTES')])
             if 'SECONDS' in TimerUnit:
 	        Seconds = int(Duration[TimerUnit.index('SECONDS')])
             #sched.add_interval_job(settimer_job, days = Days, hours=Hours, minutes=Minutes, seconds=Seconds, args=[TimerName,notifier], max_runs = 1 )
             sched.add_job(settimer_job,'interval', days = Days, hours=Hours, minutes=Minutes, seconds=Seconds, args=[TimerName,notifier] ) 

         else:
	     mic.say("I'm sorry, I did not catch that.   Please repeat again specifing the timer in seconds, minutes, hours, days")
    elif bool(re.search(r'\b(list)\b', text, re.IGNORECASE)):
	 print('we found the list')
         v = sched.get_jobs()
	 print(v)
         numjobs = len(v)
	 print(numjobs)
         if numjobs == 1:
             printstr = 'There is ' + str(numjobs) + ' timer still running'
         else:
	     printstr = 'There are ' + str(numjobs) + ' timers still running'
         print(printstr) 
	 mic.say(printstr)
         print('after print jobs')
    return



#text = text.upper()
#	 a = text.split(" ")
#	 print(a)
	 # look for the a name after the FOR command
#	 try:
#             NameLoc = a.index('FOR')+ 1
'''	     print (NameLoc)
             if a[NameLoc].isdigit():
		print("it was a digit")
                TimerName = "Basic"
	        if bool(re.search(r'\b(hours?|minutes?|days?)\b',text,re.IGNORECASE)):
 	             saystr = "The " + TimerName + " timer will be set to " + a[NameLoc] + a[NameLoc+1]
		     mic.say(saystr)
		else:
		     mic.say("I'm sorry, I did not catch that.   Please repeat again specify the timer in seconds, minutes, hours, days")
             else:
		print ("it was NOT a digit")
                TimerName = a[NameLoc]
		print(TimerName)
		saystr = "The " + TimerName + " timer will be set"
		mic.say(saystr)
         except:
	     print("FOR was not found")
             TimerName = "Basic"
	     mic.say("The timer will be set")
    return      
'''
# Look for List the timers or what timers are running
	



# parse line
  
#look for a noun after "FOR" or a number.

# looking to set a new timer

# test if user asked to set timer for

#        except:
#    elif :
#        mic.say("What phrase would you like me to repeat")
 

# 
               

def isValid(text):
    """
        Returns True if the input is related to the news.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\b(timers?|set timers?)\b', text, re.IGNORECASE))


