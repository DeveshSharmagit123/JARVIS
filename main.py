import os
import eel
from BACKEND.auth import recognize
from BACKEND.auth.recognize import AuthenticateFace
from BACKEND.feature import *
from BACKEND.command import *



def start():
    
    eel.init("FRONTEND") 
    
    play_assistant_sound()
    @eel.expose
    def init():
        eel.hideLoader()
        speak("Welcome to JARVIS")
        speak("Ready for Face Authentication")
        flag = recognize.AuthenticateFace()
        if flag ==1:
            speak("Face recognized successfully")
            eel.hideFaceAuth()
            eel.hideFaceAuthSuccess()
            speak("Welcome to Your Assistant")
            eel.hideStart()
            play_assistant_sound()
        else:
            speak("Face not recognized. Please try again")
        
    os.system('start msedge.exe --app="http://127.0.0.1:8000/index.html"')
    
    
    
    eel.start("index.html", mode=None, host="localhost", block=True) 