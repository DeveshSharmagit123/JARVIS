# import playsound
# import eel


# @eel.expose
# def playAssistantSound():
#     music_dir = "frontend\\assets\\audio\\start_sound.mp3"
#     playsound(music_dir)


from compileall import compile_path
import os
import re
from shlex import quote
import struct
import subprocess
import time
import webbrowser
import eel
from hugchat import hugchat
import pvporcupine
import pyaudio
import pyautogui
import pywhatkit as kit
import pygame
from BACKEND.command import speak
from BACKEND.config import ASSISTANT_NAME
import sqlite3

from BACKEND.helper import extract_yt_term, remove_words
conn = sqlite3.connect("JARVIS.db")
cursor = conn.cursor()
# Initialize pygame mixer
pygame.mixer.init()

# Define the function to play sound
@eel.expose
def play_assistant_sound():
    sound_file = r"FRONTEND/assets/audio/frontend_assets_audio_start_sound.mp3"
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()
    
    
def openCommand(query):
    import platform
    import webbrowser
    import os
    
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query = query.lower().strip()
    
    app_name = query.strip()
    print(f"Attempting to open: '{app_name}'")

    if app_name != "":
        try:
            # Check for web commands in the database
            try:
                print("Checking web_command table...")
                cursor.execute('SELECT url FROM web_command WHERE name=?', (app_name,))
                results = cursor.fetchall()
                print(f"Web command results: {results}")
                
                if len(results) > 0:
                    speak(f"Opening {app_name}")
                    url = results[0][0]
                    print(f"Opening URL: {url}")
                    webbrowser.open(url)
                    return
                    
            except Exception as e:
                print(f"Web command error: {e}")
            
            # Check for system commands in the database
            try:
                print("Checking sys_command table...")
                cursor.execute('SELECT path FROM sys_command WHERE name=?', (app_name,))
                results = cursor.fetchall()
                print(f"System command results: {results}")
                
                if len(results) > 0:
                    speak(f"Opening {app_name}")
                    path = results[0][0]
                    print(f"Opening path: {path}")
                    if platform.system() == "Darwin":  # macOS
                        os.system(f'open "{path}"')
                    else:
                        os.startfile(path)
                    return
                    
            except Exception as e:
                print(f"System command error: {e}")
            
            # Handle common applications directly
            if app_name == "youtube":
                speak(f"Opening YouTube")
                webbrowser.open("https://www.youtube.com")
                return
            elif app_name == "google":
                speak(f"Opening Google")
                webbrowser.open("https://www.google.com")
                return
            elif app_name == "chatgpt":
                speak(f"Opening ChatGPT")
                webbrowser.open("https://chat.openai.com")
                return
            
            # Try to open as a Mac application
            try:
                if platform.system() == "Darwin":  # macOS
                    speak(f"Trying to open {app_name}")
                    os.system(f'open -a "{app_name}"')
                else:
                    os.system(f'start {app_name}')
            except Exception as e:
                print(f"Error opening app: {e}")
                # If can't open as an app, try a web search
                speak(f"I couldn't find {app_name}. Searching the web instead.")
                webbrowser.open(f"https://www.google.com/search?q={app_name}")
                
        except Exception as e:
            print(f"Error in openCommand: {e}")
            speak("Something went wrong")

def chatBot(query):
    user_input = query.lower()
    try:
        # Check if the cookie file exists
        cookie_path = "backend/cookie.json"
        if not os.path.exists(cookie_path):
            cookie_path = "BACKEND/cookie.json"
            if not os.path.exists(cookie_path):
                # If cookie doesn't exist, provide a simple response
                print("HugChat cookie not found. Using fallback response.")
                response = "I'm sorry, I can't access my advanced knowledge right now. Is there something else I can help you with?"
                speak(response)
                return response
        
        print(f"Using cookie file at {cookie_path}")
        chatbot = hugchat.ChatBot(cookie_path=cookie_path)
        id = chatbot.new_conversation()
        chatbot.change_conversation(id)
        response = chatbot.chat(user_input)
        print(f"HugChat response: {response[:100]}...")  # Print first 100 chars
        speak(response)
        return response
    except Exception as e:
        print(f"ChatBot error: {e}")
        # Provide simple responses for common queries if HugChat fails
        if "hello" in user_input or "hi" in user_input:
            response = "Hello! How can I assist you today?"
        elif "how are you" in user_input:
            response = "I'm functioning well, thank you for asking!"
        elif "thank you" in user_input or "thanks" in user_input:
            response = "You're welcome! Is there anything else you'd like help with?"
        elif "bye" in user_input or "goodbye" in user_input:
            response = "Goodbye! Have a great day!"
        else:
            response = "I'm having trouble processing that request. Could you try again or ask something else?"
        
        speak(response)
        return response

def searchWeb(query):
    """
    Search the web for the given query
    """
    # Remove search keywords
    search_text = query.lower()
    search_text = search_text.replace("search", "").replace("google", "").replace("for", "").strip()
    
    # If the query is empty after removing search keywords
    if not search_text:
        speak("What would you like to search for?")
        return
        
    speak(f"Searching for {search_text}")
    print(f"Opening Google search for: '{search_text}'")
    
    # Perform a Google search
    try:
        search_url = f"https://www.google.com/search?q={search_text.replace(' ', '+')}"
        print(f"Opening URL: {search_url}")
        webbrowser.open(search_url)
    except Exception as e:
        print(f"Search error: {e}")
        speak("I had trouble performing that search")


def PlayYoutube(query):
    try:
        search_term = extract_yt_term(query)
        if search_term:
            speak("Playing "+search_term+" on YouTube")
            kit.playonyt(search_term)
        else:
            speak("Could not understand what to play on YouTube")
    except Exception as e:
        print(f"Error playing YouTube: {e}")
        speak("I had trouble playing that on YouTube")


def hotword():
    porcupine=None
    paud=None
    audio_stream=None
    try:
       
        # pre trained keywords    
        porcupine=pvporcupine.create(keywords=["jarvis","alexa"]) 
        paud=pyaudio.PyAudio()
        audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)
        
        # loop for streaming
        while True:
            keyword=audio_stream.read(porcupine.frame_length)
            keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)

            # processing keyword comes from mic 
            keyword_index=porcupine.process(keyword)

            # checking first keyword detetcted for not
            if keyword_index>=0:
                print("hotword detected")

                # pressing shorcut key win+j
                import pyautogui as autogui
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")
                
    except:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()


def findContact(query):
    
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT Phone FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0
    
    
def whatsApp(Phone, message, flag, name):
    

    if flag == 'message':
        target_tab = 12
        jarvis_message = "message send successfully to "+name

    elif flag == 'call':
        target_tab = 7
        message = ''
        jarvis_message = "calling to "+name

    else:
        target_tab = 6
        message = ''
        jarvis_message = "staring video call with "+name


    # Encode the message for URL
    encoded_message = quote(message)
    print(encoded_message)
    # Construct the URL
    whatsapp_url = f"whatsapp://send?phone={Phone}&text={encoded_message}"

    # Construct the full command
    full_command = f'start "" "{whatsapp_url}"'

    # Open WhatsApp with the constructed URL using cmd.exe
    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)
    
    pyautogui.hotkey('ctrl', 'f')

    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(jarvis_message)


def chatBot(query):
    try:
        user_input = query.lower()
        # Check if cookie file exists
        cookie_path = "backend/cookie.json"
        if not os.path.exists(cookie_path):
            response = "I'm having trouble accessing my knowledge. Please check if the cookie file exists."
            speak(response)
            return response
            
        chatbot = hugchat.ChatBot(cookie_path=cookie_path)
        id = chatbot.new_conversation()
        chatbot.change_conversation(id)
        response = chatbot.chat(user_input)
        print(response)
        speak(response)
        return response
    except Exception as e:
        print(f"ChatBot error: {e}")
        response = "I couldn't process that request due to a technical issue."
        speak(response)
        return response