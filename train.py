from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

# Create chatbot
chatbot = ChatBot('MyBot', storage_adapter='chatterbot.storage.SQLStorageAdapter', database_uri='sqlite:///database.sqlite3')

# Train using built-in datasets
trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train("chatterbot.corpus.english")  # Trains the bot with English conversations

print("Training complete!")
response = chatbot.get_response("Hello")
print("Chatbot:", response)
from chatterbot.trainers import ListTrainer

trainer = ListTrainer(chatbot)
trainer.train([
    "Hello",
    "Hi there! How can I assist you?",
    "What's your name?",
    "I'm your AI assistant!",
])

print("Custom training complete!")
