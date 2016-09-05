
from mic import Mic


print ("active listening")



mic = Mic("languagemodel.lm", "dictionary.dic",
              "languagemodel_persona.lm", "dictionary_persona.dic")

mic.say("How can I be of service?")

b = mic.activeListen()


#a = mic.googleTranslate()
#print(a)
