# This Python file uses the following encoding: utf-8

"""
    The Mic class handles all interactions with the microphone and speaker.
"""

import os
import json
from wave import open as open_audio
import audioop
import pyaudio
import alteration
import urllib2
import urllib
import json
import GoogleTTSFork
import time
import goslate
import random

from googleaccount import *


# quirky bug where first import doesn't work
try:
    import pocketsphinx as ps
except:
    import pocketsphinx as ps


class Mic:

    speechRec = None
    speechRec_persona = None

    def __init__(self, lmd, dictd, lmd_persona, dictd_persona, lmd_music=None, dictd_music=None):
        """
            Initiatesf the pocketsphinx instance.

            Arguments:
            lmd -- filename of the full language model
            dictd -- filename of the full dictionary (.dic)
            lmd_persona -- filename of the 'Persona' language model (containing, e.g., 'Jasper')
            dictd_persona -- filename of the 'Persona' dictionary (.dic)
        """

        hmdir = "/usr/local/share/pocketsphinx/model/hmm/en_US/hub4wsj_sc_8k"

        if lmd_music and dictd_music:
            self.speechRec_music = ps.Decoder(hmm = hmdir, lm = lmd_music, dict = dictd_music)
        self.speechRec_persona = ps.Decoder(
            hmm=hmdir, lm=lmd_persona, dict=dictd_persona)
        self.speechRec = ps.Decoder(hmm=hmdir, lm=lmd, dict=dictd)

    def transcribe(self, audio_file_path, PERSONA_ONLY=False, MUSIC=False, GOOGLE=True):
        """
            Performs STT, transcribing an audio file and returning the result.

            Arguments:
            audio_file_path -- the path to the audio file to-be transcribed
            PERSONA_ONLY -- if True, uses the 'Persona' language model and dictionary
            MUSIC -- if True, uses the 'Music' language model and dictionary
        """

        wavFile = file(audio_file_path, 'rb')
        wavFile.seek(44)

        if MUSIC:
            self.speechRec_music.decode_raw(wavFile)
            result = self.speechRec_music.get_hyp()
        elif PERSONA_ONLY:
            self.speechRec_persona.decode_raw(wavFile)
            result = self.speechRec_persona.get_hyp()
        elif GOOGLE:
            result1 = self.googleTranslate()
	    result = str(result1[0])
	    resultLangCode = "en-US"
            # Debug file
	    text_file = open("result.txt","w")
            text_file.write(str(result1[0]) + " | " + str(result1[1]) + " | " + str(result1[2]) + "\n")
	    return [ str(result) , resultLangCode ]
#           return [ str(result) ]
#            return[0]

	else:
            self.speechRec.decode_raw(wavFile)
            result = self.speechRec.get_hyp()

        print "==================="
        print "JASPER: " + result[0]
        print "==================="

#        return [result[0], "en-US"]
        return [result[0], "en-US"]



    def getScore(self, data):
        rms = audioop.rms(data, 2)
        score = rms / 3
        return score

    def fetchThreshold(self):

        # TODO: Consolidate all of these variables from the next three
        # functions
        THRESHOLD_MULTIPLIER = 1.8
        AUDIO_FILE = "passive.wav"
        RATE = 16000
        CHUNK = 1024

        # number of seconds to allow to establish threshold
        THRESHOLD_TIME = 1

        # number of seconds to listen before forcing restart
        LISTEN_TIME = 10

        # prepare recording stream
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

        # stores the audio data
        frames = []

        # stores the lastN score values
        lastN = [i for i in range(20)]

        # calculate the long run average, and thereby the proper threshold
        for i in range(0, RATE / CHUNK * THRESHOLD_TIME):

            data = stream.read(CHUNK)
            frames.append(data)

            # save this data point as a score
            lastN.pop(0)
            lastN.append(self.getScore(data))
            average = sum(lastN) / len(lastN)

        # this will be the benchmark to cause a disturbance over!
        THRESHOLD = average * THRESHOLD_MULTIPLIER

        return THRESHOLD

    def passiveListen(self, PERSONA):
        """
            Listens for PERSONA in everyday sound
            Times out after LISTEN_TIME, so needs to be restarted
        """

        THRESHOLD_MULTIPLIER = 1.8
        AUDIO_FILE = "passive.wav"
        RATE = 16000
        CHUNK = 1024

        # number of seconds to allow to establish threshold
        THRESHOLD_TIME = 1

        # number of seconds to listen before forcing restart
        LISTEN_TIME = 20

        # prepare recording stream
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

        # stores the audio data
        frames = []

        # stores the lastN score values. Initialize to zero.
        lastN = [0 for i in range(RATE/CHUNK * THRESHOLD_TIME)]

        # calculate the long run average, and thereby the proper threshold
        for i in range(0, RATE / CHUNK * THRESHOLD_TIME):

            data = stream.read(CHUNK)
            frames.append(data)

            # save this data point as a score
            lastN.pop(0)
            lastN.append(self.getScore(data))
            average = sum(lastN) / len(lastN)

        # this will be the benchmark to cause a disturbance over!
        THRESHOLD = average * THRESHOLD_MULTIPLIER
	print("Threshold is ", THRESHOLD)
        # save some memory for sound data
        #frames = []

        # flag raised when sound disturbance detected
        didDetect = False
	print("listening passively for threshold")
        # start passively listening for disturbance above threshold
        for i in range(0, RATE / CHUNK * LISTEN_TIME):

            data = stream.read(CHUNK)
            frames.append(data)
            score = self.getScore(data)

            if score > THRESHOLD:
                didDetect = True
		print("threshold detected", score)
                break

        # no use continuing if no flag raised
        if not didDetect:
            print "No disturbance detected"
            return

        # cutoff any recording before this disturbance was detected
        frames = frames[-20:]

        # otherwise, let's keep recording for few seconds and save the file
        DELAY_MULTIPLIER = 1
        for i in range(0, RATE / CHUNK * DELAY_MULTIPLIER):

            data = stream.read(CHUNK)
            frames.append(data)

        # save the audio data
        stream.stop_stream()
        stream.close()
        audio.terminate()
        write_frames = open_audio(AUDIO_FILE, 'wb')
        write_frames.setnchannels(1)
        write_frames.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        write_frames.setframerate(RATE)
        write_frames.writeframes(''.join(frames))
        write_frames.close()
	print("checking if persona was said")
	start_time = time.time()
        # check if PERSONA was said
        transcribed = self.transcribe(AUDIO_FILE, PERSONA_ONLY=True)
        print(time.time()-start_time, "Seconds")
        #print(transcribed)
	#print(PERSONA)
        if PERSONA in transcribed[0]:
	    print("persona was found")
            return (THRESHOLD, PERSONA)

        return (False, transcribed)

    def activeListen(self, THRESHOLD=None, LISTEN=True, MUSIC=False, GOOGLE=False):
        """
            Records until a second of silence or times out after 12 seconds
        """

        AUDIO_FILE = "active.wav"
        RATE = 16000
        CHUNK = 1024
        LISTEN_TIME = 7

        # user can request pre-recorded sound
        if not LISTEN:
            if not os.path.exists(AUDIO_FILE):
                return None

            return self.transcribe(AUDIO_FILE)

        # check if no threshold provided
        if THRESHOLD == None:
            THRESHOLD = self.fetchThreshold()

#       os.system("aplay -D hw:1,0 beep_hi.wav")
#    aT some point I should make this programable         
        self.ericaResponse()

        # prepare recording stream
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

        frames = []
        print(THRESHOLD,"threshold")
        # increasing the range # results in longer pause after command
        # generation
        lastN = [THRESHOLD * 1.2 for i in range(40)]

        for i in range(0, RATE / CHUNK * LISTEN_TIME):

            data = stream.read(CHUNK)
            frames.append(data)
            score = self.getScore(data)
	    #print(score,"score")

            lastN.pop(0)
            lastN.append(score)

            average = sum(lastN) / float(len(lastN))
            print(average,"average")

            # TODO: 0.8 should not be a MAGIC NUMBER!
	    # we want to wait for user to stop speaking for a little while.    
            if average < THRESHOLD * .75:
                break

#        os.system("aplay -D hw:1,0 beep_lo.wav")
# at some point, this should programable
        self.analyzeResponse()

        # save the audio data
        stream.stop_stream()
        stream.close()
        audio.terminate()
        write_frames = open_audio(AUDIO_FILE, 'wb')
        write_frames.setnchannels(1)
        write_frames.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        write_frames.setframerate(RATE)
        write_frames.writeframes(''.join(frames))
        write_frames.close()
        print ("wrote to active.wave")

        # DO SOME AMPLIFICATION
        # os.system("sox "+AUDIO_FILE+" temp.wav vol 20dB")

        if MUSIC:
            return self.transcribe(AUDIO_FILE, MUSIC=True)[0]

	if GOOGLE:
            return self.transcribe(AUDIO_FILE, GOOGLE=True)

        return self.transcribe(AUDIO_FILE)[0]
        
    def say(self, phrase, OPTIONS=" -vdefault+f3 -p 40 -s 160 --stdout > say.wav"):
        # alter phrase before speaking
        phrase = alteration.clean(phrase)

        os.system("espeak " + json.dumps(phrase) + OPTIONS)
#       send phrase to google and it retuns an MP3. we use mpg123 to conver to wav
#        outfile = open ("say.mp3","w")
#        GoogleTTSFork.GoogleTTS(phrase,outfile)
        
        os.system("aplay -D hw:1,0 say.wav")


    def googleTranslate(self, langCode='en-US'):
	    """
		This Function Translates Speech to text from
		 english or polish into english for JASPER

		It can be adapted for any language supported by google
		 by changing profile.yaml to any language code from
		 the list found at:
		 https://developers.google.com/translate/v2/using_rest#language-params
	    """
	    starttime = time.time()
	    gs = goslate.Goslate()
            RATE = 16000
            os.system("avconv -y -i active.wav -ar 16000 -acodec flac active.flac")
	    converttime = time.time() - starttime
            flac = open("active.flac", 'rb')
            data = flac.read()
            flac.close()
            print("finished converting to flac")
            # The following is in google account global parameter.   
            url = googleaccounturl

    	    try:
                req = urllib2.Request(
		    url,
                    data=data,
                    headers={
                        'Content-type': 'audio/x-flac; rate=%s' % RATE})
                response_url = urllib2.urlopen(req)
                response_read = response_url.read()
                response_read = response_read.decode('utf-8')
            except urllib2.URLError:
	        print("we have an error calling google")
                return [ "no_info" , 0 , str(langCode) ]
            if response_read:
	        translatetime = time.time() - starttime - converttime
		jsdata = None
                try:
		    allData = response_read.splitlines()
                    # the second line is a proper json object
                    jsdata = json.loads(allData[1])
		    print (allData)
		    #for line in allData:
			# This is specific to the json returned by google.
			# Debug File
#                    	text_file = open("json.txt","w")
                    	#text_file.write(line)

#			jsdata = json.loads( response_read )

#			text_file.close()

			#try:
			    #if jsdata == None:
				#jsdata = json.loads(line)
			    #if jsdata["status"] == 5:
				#jsdata = None
			#except:
			    #pass

                    if not jsdata:
                        return [ "no_info" , 0 , str(langCode) ]

		    #text_file = open("json.txt","w")
		    #text_file.write(str(jsdata))
		    #text_file.close()

		    result = jsdata['result'][0]['alternative'][0]['transcript']
                    try:
                        confidence = jsdata['result'][0]['alternative'][0]['confidence']
		    except:
		        confidence = .99
 
                    print "==================="
                    print "JASPER: " + result
                    print "==================="
		    print (converttime, "converttime")
		    print (translatetime , "translate")

		    return [ str(result), float(confidence), str(langCode) ]
                except IndexError:
		    return [ "no_info" , 0 , str(langCode) ]
            else:
                return [ "no_info" , 0 , str(langCode) ]

    def ericaResponse(self):
        sayings= ['Yes Master','Go Ahead','What is up', 'say your command....', 'how can I help','what do you want now?','say you command', 'what is your wish' ]
        styleSaying = random.choice(sayings)
        self.say(styleSaying)
        return

    def analyzeResponse(self):
        sayings= ['Analyzing response', 'just a second', 'checking', 'hold on', 'please be patient']
        styleSaying = random.choice(sayings)
        self.say(styleSaying)
        return

