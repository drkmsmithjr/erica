#!/usr/bin/python

import sys
import os
import argparse
import re
import urllib, urllib2
import time
import time

def GoogleTTS(text, outputMP3file):

    # text will be converter to speech using googles TTS api
    # the outputs will be both MP3 and WAV formats

#    description='Google TTS Downloader.'
#    parser = argparse.ArgumentParser(description=description,
#                                     epilog='tunnel snakes rule')

#    parser.add_argument('-o','--output',action='store',nargs='?',
#                        help='Filename to output audio to',
#                        type=argparse.FileType('w'), default='out.mp3')
#    parser.add_argument('-l','--language', action='store', nargs='?',help='Language to output text to.',default='en')
#    group = parser.add_mutually_exclusive_group(required=True)
#    group.add_argument('-f','--file',type=argparse.FileType('r'),help='File to read text from.')
#    group.add_argument('-s', '--string',action='store',nargs='+',help='A string of text to convert to speech.')

#    if len(sys.argv)==1:
#       parser.print_help()
#       sys.exit(1)

#    args = parser.parse_args()
#    if args.file:
#        text = args.file.read()
#    if args.string:
#        text = ' '.join(map(str,args.string))

    #process text into chunks.  remove some unicode parameters.
    print("text before", text)
    text = text.replace('\n','')
    #print(text)
    # this command is used to ignore any non-ascii characters in the string.   
    text.encode('ascii','ignore')
    print(text)
    text_list = re.split('(\,|\.)', text)
    combined_text = []
    for idx, val in enumerate(text_list):
        if idx % 2 == 0:
            combined_text.append(val)
        else:
            joined_text = ''.join((combined_text.pop(),val))
            if len(joined_text) < 100:
                combined_text.append(joined_text)
            else:
                subparts = re.split('( )', joined_text)
                temp_string = ""
                temp_array = []
                for part in subparts:
                    temp_string = temp_string + part
                    if len(temp_string) > 80:
                        temp_array.append(temp_string)
                        temp_string = ""
                #append final part
                temp_array.append(temp_string)
                combined_text.extend(temp_array)
    #download chunks and write them to the output file
    print("after chucking text", combined_text)
    
    start_time = time.time()    
    for idx, val in enumerate(combined_text):
        mp3url = "http://translate.google.com/translate_tts?tl=en&q=%s&total=%s&idx=%s" % (urllib.quote_plus(val), len(combined_text), idx)
        headers = {"Host":"translate.google.com",
          "Referer":"http://www.gstatic.com/translate/sound_player2.swf",
          "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.163 Safari/535.19"}
        req = urllib2.Request(mp3url, '', headers)
        sys.stdout.write('.')
        sys.stdout.flush()
        if len(val) > 0:
            try:
                response = urllib2.urlopen(req)
                outputMP3file.write(response.read())
#                time.sleep(.2)
            except urllib2.HTTPError as e:
                print ('%s' % e)
    outputMP3file.close()

    #convert mp3 file name to wav
    mp3 = outputMP3file.name
    # copying the string minus the mp3 then adding wav
    wav = mp3[0:mp3.find("mp3")] + "wav"
    commandcall = "mpg123 -w " + wav + " " + mp3
    os.system(commandcall)
    print('Saved MP3 to %s and WAV to %s' % (mp3,  wav))
    print (time.time() - start_time, "seconds")
#outfile = open("Out5.mp3","w")
#GoogleTTS("sweet butt", outfile)
