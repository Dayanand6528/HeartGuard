import urllib.request
import urllib.error
import json
import re

class OllamaMedicalChatbot:
    def __init__(self, model_name="llama3.2:3b", ollama_url="http://localhost:11434/api/chat"):
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.system_prompt = (
            "You are HeartGuard AI, an expert medical and healthcare AI assistant.\n\n"
            "STRICT BOUNDARY RULES:\n"
            "1. You MUST ONLY answer questions related to medicine, healthcare, cardiology, clinical biomarkers, diseases, medical symptoms, pharmacology, human anatomy, medical diet, and health wellness.\n"
            "2. IF THE USER ASKS ABOUT NON-MEDICAL TOPICS (such as computer programming/coding, sports, movies, entertainment, politics, history, general trivia, finance, weather, non-medical writing, etc.), YOU MUST REFUSE TO ANSWER. Respond politely: 'I am HeartGuard AI, a dedicated medical assistant. I can only answer questions related to health, medicine, and clinical care. Please ask a medical query.'\n"
            "3. DO NOT USE ASTERISKS (*) IN YOUR RESPONSE. Do not use markdown bold or italic asterisks (* or **). Write in clean plain text with standard bullet points (- or numbers).\n"
            "4. Provide clear, accurate, professional, and direct medical advice."
        )

    def get_response(self, user_message):
        if not user_message or not user_message.strip():
            return "Please type a valid medical question or health concern."

        text = user_message.strip()

        # Fast local pre-check for obvious non-medical coding/sports/trivia triggers
        non_medical_keywords = [
            "python code", "javascript code", "java code", "html code", "css code",
            "write code", "programming", "software bug", "who won the game",
            "world cup", "football match", "cricket match", "movie recommendation",
            "capital of", "weather in", "tell me a joke"
        ]
        if any(kw in text.lower() for kw in non_medical_keywords):
            return "I am HeartGuard AI, a dedicated medical assistant. I can only answer questions related to health, medicine, and clinical care. Please ask a medical query."

        # Call local Medical AI API
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": text}
            ],
            "stream": False
        }

        try:
            req = urllib.request.Request(
                self.ollama_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=45) as response:
                result_data = json.loads(response.read().decode("utf-8"))
                reply = result_data.get("message", {}).get("content", "")
                
                # Clean any remaining asterisks
                reply = reply.replace("*", "")
                return reply.strip()

        except urllib.error.URLError as e:
            return "Connection error: Could not reach local Medical AI service. Please ensure the local Medical AI engine is running."
        except Exception as e:
            return f"Error generating medical response: {str(e)}"

# Global chatbot instance
chatbot_instance = OllamaMedicalChatbot()

def get_bot_response(message):
    return chatbot_instance.get_response(message)
