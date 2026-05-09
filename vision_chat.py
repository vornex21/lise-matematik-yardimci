import openai
import base64
import os
import json
import shutil
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
        try:
            content = [{"type": "text", "text": question}]

            if image:
                # Görseli base64'e çevir
                import io
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{img_str}"}
                })

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Sen yardımcı bir matematik öğretmenisin. Soruları adım adım ve anlaşılır şekilde çöz."},
                    {"role": "user", "content": content}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            self.messages.append({"role": "user", "content": question})
            self.messages.append({"role": "assistant", "content": answer})
            self.save_history()
            
            return answer

        except Exception as e:
            return f"Hata oluştu: {str(e)}"
