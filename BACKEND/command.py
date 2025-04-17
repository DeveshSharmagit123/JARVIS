import time
import pyttsx3
import speech_recognition as sr
import eel

def speak(text):
    text = str(text)
    engine = pyttsx3.init()  # Use default driver instead of 'sapi5'
    voices = engine.getProperty('voices')
    # print(voices)
    # Use a voice that exists on your system (index might be different on Mac)
    engine.setProperty('voice', voices[0].id)  
    eel.DisplayMessage(text)
    engine.say(text)
    engine.runAndWait()
    engine.setProperty('rate', 174)
    eel.receiverText(text)

# Expose the Python function to JavaScript

def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("I'm listening...")
        eel.DisplayMessage("I'm listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, 10, 8)

    try:
        print("Recognizing...")
        eel.DisplayMessage("Recognizing...")
        query = r.recognize_google(audio, language='en-US')
        print(f"User said: {query}\n")
        eel.DisplayMessage(query)
        
        
        speak(query)
    except Exception as e:
        print(f"Error: {str(e)}\n")
        return None

    return query.lower()



@eel.expose
def takeAllCommands(message=None):
    if message is None:
        query = takecommand()  # If no message is passed, listen for voice input
        if not query:
            return  # Exit if no query is received
        print(query)
        eel.senderText(query)
    else:
        query = message  # If there's a message, use it
        print(f"Message received: {query}")
        eel.senderText(query)
    
    try:
        if query:
            query_lower = query.lower()
            print("Processing query:", query)
            
            # Check for search commands
            if "search" in query_lower or "google" in query_lower and "for" in query_lower:
                print("Attempting to search the web")
                from BACKEND.feature import searchWeb
                searchWeb(query)
            # Check for open commands
            elif "open" in query_lower:
                print("Attempting to open command")
                from BACKEND.feature import openCommand
                openCommand(query)
            elif "play" in query.lower() and "youtube" in query.lower():
                print("Attempting to play YouTube")
                from BACKEND.feature import PlayYoutube
                PlayYoutube(query)
            elif "send message" in query.lower() or "call" in query.lower() or "video call" in query.lower():
                print("Attempting to handle contacts")
                from BACKEND.feature import findContact, whatsApp
                flag = ""
                Phone, name = findContact(query)
                if Phone != 0:
                    if "send message" in query:
                        flag = 'message'
                        speak("What message to send?")
                        query = takecommand()  # Ask for the message text
                    elif "call" in query:
                        flag = 'call'
                    else:
                        flag = 'video call'
                    whatsApp(Phone, query, flag, name)
            else:
                print("Attempting to use chatBot")
                from BACKEND.feature import chatBot
                chatBot(query)
        else:
            speak("No command was given.")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()  # This will print the full stack trace
        speak("Sorry, something went wrong.")
    
    eel.ShowHood()