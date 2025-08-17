# chatbot/test_chatbot.py
from penny_chatbot import PennyChatbot

if __name__ == "__main__":
    # Replace '1' with the actual user_id from your database
    chatbot = PennyChatbot(user_id=1)
    chatbot.chat()
