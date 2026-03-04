import openai
import base64
import os
import json
import shutil

from pylatexenc.latex2text import LatexNodes2Text

import streamlit as st

openai.api_key = st.secrets["OPENAI_API_KEY"]
# buradan sonrası sınıf ve fonksiyonlar
def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def copy_image_to_log_folder(image_path, dest_folder, index):
    if not image_path or not os.path.exists(image_path):
        return None
    ext = os.path.splitext(image_path)[1]
    new_filename = f"image_{index}{ext}"
    new_path = os.path.join(dest_folder, new_filename)
    shutil.copy(image_path, new_path)
    return new_filename

class VisionChatWithMemory:
    def __init__(self, log_dir):
        self.messages = []
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.history_path = os.path.join(self.log_dir, "chat_history.json")
        self.load_history()

    def load_history(self):
        if os.path.exists(self.history_path):
            with open(self.history_path, "r", encoding="utf-8") as f:
                saved = json.load(f)
                self.messages = saved.get("messages", [])
        else:
            self.messages = []

    def save_history(self):
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump({"messages": self.messages}, f, indent=2, ensure_ascii=False)

    def ask_new_question(self, question, image=None):
        if not question.strip():
            raise ValueError("Soru boş olamaz.")

        q_number = len([m for m in self.messages if m["role"] == "user"]) + 1

        image_filename = None
        if image:
            image_filename = f"question_{q_number}.png"
            full_path = os.path.join(self.log_dir, image_filename)
            image.save(full_path)

        content = [{"type": "text", "text": question}]
        if image_filename:
            with open(os.path.join(self.log_dir, image_filename), "rb") as f:
                base64_img = base64.b64encode(f.read()).decode("utf-8")
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{base64_img}"}
            })

        self.messages.append({"role": "user", "content": content, "image_filename": image_filename})

        # Son 9 görseli önceki sorulardan ekle
        prev_user_messages = [m for m in self.messages if m["role"] == "user"]
        prev_images = []
        for m in reversed(prev_user_messages[:-1]):
            if len(prev_images) >= 9:
                break
            fname = m.get("image_filename")
            if fname:
                full_path = os.path.join(self.log_dir, fname)
                if os.path.exists(full_path):
                    with open(full_path, "rb") as f:
                        base64_prev = base64.b64encode(f.read()).decode("utf-8")
                    prev_images.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_prev}"}
                    })

        content.extend(prev_images)

        # GPT-4o çağrısı (2024-2025 sonrası syntax)
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=self.messages,
            max_tokens=500
        )

        answer = response.choices[0].message.content
        print(f"\nSoru: {question}\nCevap: {LatexNodes2Text().latex_to_text(answer)}")

        self.messages.append({"role": "assistant", "content": answer})

        if len(self.messages) > 20:
            self.messages = self.messages[-20:]

        self.save_history()

        return answer

