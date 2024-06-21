from flask import Flask, render_template, request, jsonify
import json
from difflib import get_close_matches
import datetime
import requests
import webbrowser
from bs4 import BeautifulSoup
import re
from googlesearch import search as google_search
import codecs
import pyttsx3
import time

app = Flask(__name__)

# Constants
KNOWLEDGE_FILE = r"C:\Users\Rufus K Manoj\Downloads\knowledge\knowledge1.json"
SIMILARITY_CUTOFF = 0.8

# Load knowledge base from JSON file
def load_knowledge_base(file_path: str) -> dict:
    try:
        with codecs.open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        data = {"questions": []}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{file_path}': {e}")
        data = {"questions": []}
    except Exception as e:
        print(f"Unexpected error loading knowledge base: {e}")
        data = {"questions": []}
    return data

# Save knowledge base to JSON file
def save_knowledge_base(file_path: str, data: dict):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)
    except IOError as e:
        print(f"Error saving knowledge base: {e}")

# Find the best match for user input question
def find_best_match(user_question: str, questions: list[str]) -> str | None:
    matches = get_close_matches(user_question.lower(), questions, n=1, cutoff=SIMILARITY_CUTOFF)
    return matches[0] if matches else None

# Get answer for the given question from knowledge base
def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base["questions"]:
        if q["question"].lower() == question.lower():
            return q["answer"]
    return None

# Function to get current time and date
def get_current_time_date():
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%Y-%m-%d")
    return f"Current time is {current_time}, and today's date is {current_date}."

# Function to get weather information
API_KEY = "29d30a157e2ec41f1fb244bfdb58153a"
def get_weather_info():
    api_url = "http://api.openweathermap.org/data/2.5/weather"  
    params = {  
        "id":"1254335",  
        "units": "metric",  
        "appid":"29d30a157e2ec41f1fb244bfdb58153a"  
    }  
    response = requests.get(api_url, params=params)  
    data = response.json()  
    report = "Weather Report:\n"  
    city = data["name"]  
    report += f"City: {city}\n"  
    temperature = data["main"]["temp"]  
    report += f"Temperature: {temperature}°C\n"  
    humidity = data["main"]["humidity"]  
    report += f"Humidity: {humidity}%\n"  
    wind_speed = data["wind"]["speed"]  
    report += f"Wind Speed: {wind_speed} m/s\n"  
    return report  
  
 



# Function to search and play the most popular video on YouTube
def play_most_popular_video(query):
    try:
        youtube_search_url = f"https://www.youtube.com/results?search_query={query}"
        response = requests.get(youtube_search_url)
        response.raise_for_status()

        match = re.search(r'/watch\?v=(\S+)', response.text)
        if match:
            video_id = match.group(1)
            video_link = f"https://www.youtube.com/watch?v={video_id}"
            webbrowser.open(video_link)
            return f"Playing most popular video for '{query}' on YouTube."
        else:
            return "No video found for the query."

    except requests.RequestException as e:
        print(f"Error performing YouTube search: {e}")
        return "Could not perform YouTube search at the moment."
    except Exception as e:
        print(f"Error playing YouTube video: {e}")
        return "Could not play video at the moment."

# Placeholder function to play most popular song (without Spotify API)
def play_most_popular_song(query):
    try:
        search_results = google_search(query + "song"+"spotify", num=1, stop=1, pause=2)
        song_url = next(search_results)
        webbrowser.open(song_url)
        return f"Playing: {query} On Spotify!"
    except Exception as e:
        return f"Sorry, unable to play the song: {str(e)}"
    
# Speak the given text
def speak(text, voice_id=None, rate=2000):
    if len(text)<100:
        engine = pyttsx3.init()
        engine.setProperty('rate', rate)  # Set the speaking rate
        if voice_id:
            engine.setProperty('voice', voice_id)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    

# Render the index.html template
@app.route('/')
def index():
    return render_template('index.html')

# Handle incoming messages
@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.json
    user_input = data.get('message', '').strip()

    if user_input.lower() == "quit":
        return jsonify({'answer': "Goodbye!"})

    knowledge_base = load_knowledge_base(KNOWLEDGE_FILE)

    if "time" in user_input.lower() :
        answer = get_current_time_date()
    elif "weather" in user_input.lower() :
        answer = get_weather_info()
    elif user_input.lower().startswith("play song"):
        query = user_input[len("play song"):].strip()
        answer = play_most_popular_song(query)
    elif user_input.lower().startswith("play"):
        query = user_input[len("play"):].strip()
        answer = play_most_popular_video(query)
    else:
        best_match = find_best_match(user_input, [q["question"].lower() for q in knowledge_base["questions"]])

        if best_match:
            answer = get_answer_for_question(best_match, knowledge_base)
            if not answer:
                webbrowser.open(f"https://www.google.com/search?q={user_input}&rlz=1C1RXQR_enIN1025IN1025&ie=UTF-8")
                answer = f"I have no data trained on '{best_match}'. Opening Google search."
        else:
            webbrowser.open(f"https://www.google.com/search?q={user_input}&rlz=1C1RXQR_enIN1025IN1025&ie=UTF-8")
            answer = f"I have no data trained on '{user_input}'. Opening Google search."

    # Return the answer first
    response = jsonify({'answer': answer})
    
    # Add a delay before speaking
    time.sleep(0.4)

    # Speak the answer at a slower rate
    speak(answer, voice_id=r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_Guy_11.0', rate=160)

    return response

if __name__ == '__main__':
    app.run(debug=True)
