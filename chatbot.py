# chatbot.py

import google.generativeai as genai

class Chatbot:

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):

        if not api_key:
            raise ValueError("API anahtarı boş olamaz. Lütfen bir API anahtarı sağlayın.")
            
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
            self.chat = self.model.start_chat(history=[])
            print(f"✅ Standart Chatbot, '{model_name}' modeli ile başarıyla başlatıldı.")
        except Exception as e:
            print(f"❌ Chatbot başlatılırken bir hata oluştu: {e}")
            raise

    def send_message(self, message: str) -> str:

        if not message.strip():
            return "Lütfen bir mesaj girin."
            
        try:
            response = self.chat.send_message(message)
            return response.text
        except Exception as e:
            print(f"❌ Mesaj gönderilirken bir hata oluştu: {e}")
            return "Üzgünüm, bir sorunla karşılaştım. Lütfen daha sonra tekrar deneyin."