from flask import Flask, render_template, request, jsonify
import os
import speech_recognition as sr
from gtts import gTTS
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Ensure the 'static/audio' directory exists
AUDIO_FOLDER = 'static/audio'
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

# Initialize the chatbot
chatbot = ChatBot('GirlVoiceChatbot', storage_adapter='chatterbot.storage.SQLStorageAdapter', database_uri='sqlite:///database.sqlite3')
trainer = ChatterBotCorpusTrainer(chatbot)

# Train the chatbot only if the database is empty
if not os.path.exists('database.sqlite3'):
    trainer.train("chatterbot.corpus.english")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.form['user_input']
    
    if not user_input.strip():
        return jsonify({'response': 'Please enter a message.'})
    
    # Get the chatbot's response
    bot_response = chatbot.get_response(user_input).text
    
    # Convert the bot's response to speech
    tts = gTTS(text=bot_response, lang='en', slow=False)
    unique_filename = f"response_{uuid.uuid4().hex}.mp3"
    audio_file = os.path.join(AUDIO_FOLDER, unique_filename)
    tts.save(audio_file)
    
    # Return the bot's response and the path to the audio file
    return jsonify({'response': bot_response, 'audio_url': '/' + audio_file})

@app.route('/speech_to_text', methods=['POST'])
def speech_to_text():
    recognizer = sr.Recognizer()
    
    # Get the audio file from the request
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    
    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not audio_file.filename.lower().endswith(('.wav', '.mp3', '.ogg')):
        return jsonify({'error': 'Invalid file format'}), 400
    
    audio_path = os.path.join(AUDIO_FOLDER, f'user_audio_{uuid.uuid4().hex}.wav')
    audio_file.save(audio_path)
    
    # Convert speech to text
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
        try:
            user_input = recognizer.recognize_google(audio_data)
            return jsonify({'text': user_input})
        except sr.UnknownValueError:
            return jsonify({'text': 'Sorry, I could not understand that.'})
        except sr.RequestError:
            return jsonify({'text': 'Could not request results from Google Speech Recognition service.'})

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    chatbot.storage.drop()
    return jsonify({'message': 'Chat history cleared successfully.'})

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1']
    app.run(debug=debug_mode)