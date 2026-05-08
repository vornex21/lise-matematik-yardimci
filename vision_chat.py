import os
import json
import shutil
import tempfile
from datetime import datetime

class VisionChatWithMemory:
    def __init__(self, log_dir):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.history_path = os.path.join(log_dir, "chat_history.json")
        self.messages = []
        self.load_history()

    def load_history(self):
        if os.path.exists(self.history_path):
            with open(self.history_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.messages = data.get("messages", [])
    
    def save_history(self):
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump({"messages": self.messages}, f, ensure_ascii=False, indent=2)

    def ask_new_question(self, question, image=None):
        # Basit versiyon - şu an app.py içinde Gemini çağrısı yapıyoruz
        # İleride burayı da geliştirebiliriz
        self.messages.append({"role": "user", "content": question})
        self.save_history()
        return "Bu fonksiyon şu anda app.py üzerinden yönetiliyor."
