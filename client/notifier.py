import Queue
from modules import Gmail
from apscheduler.scheduler import Scheduler
import logging
logging.basicConfig()
from random import randint
import datetime
from semantic.dates import DateService
from modules.app_utils import getTimezone


class Notifier(object):

    class NotificationClient(object):

        def __init__(self, gather, timestamp):
            self.gather = gather
            self.timestamp = timestamp

        def run(self):
            self.timestamp = self.gather(self.timestamp)

    def __init__(self, profile):
        self.q = Queue.Queue()
        self.profile = profile
        self.notifiers = [
            self.NotificationClient(self.handleEmailNotifications, None), self.NotificationClient(self.handleHourNotifications, None),]
	self.notifiersTimeCrit = [self.NotificationClient(self.handleTimerNotifications, None),]
        print("INITIALIZING THE TIMER EVENTS")
	print("++++++++++++++++++++++++++++++")
	print("++++++++++++++++++++++++++++++")
	print("++++++++++++++++++++++++++++++")
	print("++++++++++++++++++++++++++++++")
	print("++++++++++++++++++++++++++++++")
	
        #slow scheduler for non essential events
        sched = Scheduler()
        sched.start()
        sched.add_interval_job(self.gather, seconds=30)

        #fast scheduler for time critical notifications like timers
        sched2 = Scheduler()
	sched2.start()
	sched.add_interval_job(self.gatherTimeCrit ,seconds=1)


    def gatherTimeCrit(self):
        #print("i'm in time crite gather circuit")
        #[client.run() for client in self.notifiersTimeCrit]
	#print("i'm out of the gather circuit")
        return

    def timerDone(self,TimerName):
        # name of the timer that was done
        # list of announcement sayings
        saying = ['Hello there ']
        saying.append('Hello There, Excuse Me Please..')
	saying.append('May I have your Attention Please..')
        x = randint(0,len(saying)-1)
        styleTimerDone = saying[x] + " The " + TimerName + " Timer is complete"
	self.q.put(styleTimerDone)
	return


    def gather(self):
        #print("i'm in gather circuit")
        [client.run() for client in self.notifiers]
	#print("i'm out of the gather circuit")

    def handleEmailNotifications(self, lastDate):
        """Places new Gmail notifications in the Notifier's queue.
	We place a limit of 50 unread emails at a time """

        emails = Gmail.fetchUnreadEmails(self.profile, since=lastDate)
#	print(emails)
	print("inside the email notification routine")
        if emails:
            lastDate = Gmail.getMostRecentDate(emails)
        def styleEmail(e):
            return "New email from %s." % Gmail.getSender(e)
        for e in emails:
            self.q.put(styleEmail(e))
        return lastDate

    def handleTimerNotifications(self, lastDate):
        """Places new Gmail notifications in the Notifier's queue."""
	print(lastDate)
	print("inside the timer notification routine")
        return lastDate


    def handleHourNotifications(self, nextHour):
        """Announces the time of day
        At each hour annoice the time of day.   
        We need ensure Nexthour occurs at a given hour interval.
        Then test for the next hour change within one hour of last date.
        get the hour now
        determine if time now matches the next hour
        if it is then put a notification onto the queue
        set the next hour increase by one or if 23 then set to 24.
        """
        # get the current time
        tz = getTimezone(self.profile)
        now = datetime.datetime.now(tz=tz)
         
#	test to see if this is the first time running the program
	if nextHour == None:
            # set the next hour
	    min = now.minute
	    sec = now.second
	    mic = now.microsecond
	    nextHour = now + datetime.timedelta(hours=1,seconds=-sec,minutes=-min,microseconds=-mic)
        
        if now > nextHour: 
            service = DateService()
            response = service.convertTime(nextHour)
            styleHour = "It is " + response + " right now."
            self.q.put(styleHour)
            # reset the next hour
	    min = now.minute
	    sec = now.second
	    mic = now.microsecond
	    nextHour = now + datetime.timedelta(hours=1,seconds=-sec,minutes=-min,microseconds=-mic)
              
	print(nextHour)
	print("inside the Hour Notification routine")
        return nextHour



    def getNotification(self):
        """Returns a notification. Note that this function is consuming."""
        try:
            notif = self.q.get(block=False)
            return notif
        except Queue.Empty:
            return None

    def getAllNotifications(self):
        """
            Return a list of notifications in chronological order.
            Note that this function is consuming, so consecutive calls
            will yield different results.
        """
        notifs = []

        notif = self.getNotification()
        while notif:
            notifs.append(notif)
            notif = self.getNotification()

        return notifs
