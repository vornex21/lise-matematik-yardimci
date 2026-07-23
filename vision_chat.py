import openai
import anthropic
import base64
import os
import json
import io
from datetime import datetime
from PIL import Image

class VisionChatWithMemory:
    def __init__(self, log_dir="chat_logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.history_path = os.path.join(log_dir, "chat_history.json")
        self.messages = []
        self.load_history()

    def load_history(self):
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.messages = data.get("messages", [])
            except:
                self.messages = []

    def save_history(self):
        try:
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump({"messages": self.messages}, f, ensure_ascii=False, indent=2)
        except:
            pass

    def get_system_prompt(self, subject="Genel Matematik"):
        prompts = {
            "Cebir": "Sen uzman bir Cebir öğretmenisin. Adım adım ve anlaşılır şekilde çöz.",
            "Geometri": "Sen uzman bir Geometri öğretmenisin. Görsel analizlerde güçlü ol.",
            "Türev ve İntegral": "Sen ileri seviye Kalkülüs öğretmenisin.",
            "Olasılık": "Sen olasılık ve istatistik uzmanısın.",
            "Genel Matematik": "Sen yardımcı bir matematik öğretmenisin. Adım adım çöz."
        }
        return prompts.get(subject, prompts["Genel Matematik"])

    def ask_new_question(self, question, image=None, provider="openai", model="gpt-4o-mini", subject="Genel Matematik"):
        try:
            system_prompt = self.get_system_prompt(subject)

            if provider == "openai":
                content = [{"type": "text", "text": question}]
                if image:
                    buffered = io.BytesIO()
                    image.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img_str}"}
                    })

                client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": content}
                    ],
                    max_tokens=1200,
                    temperature=0.7,
                )
                answer = response.choices[0].message.content

            elif provider == "claude":
                client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
                if image:
                    # Claude için base64
                    buffered = io.BytesIO()
                    image.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    content = [
                        {"type": "text", "text": question},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": img_str
                            }
                        }
                    ]
                else:
                    content = question

                response = client.messages.create(
                    model=model,
                    max_tokens=1200,
                    temperature=0.7,
                    system=system_prompt,
                    messages=[{"role": "user", "content": content}]
                )
                answer = response.content[0].text

            else:
                answer = "Desteklenmeyen provider."

            # Geçmişe kaydet
            self.messages.append({"role": "user", "content": f"[{subject}] {question}"})
            self.messages.append({"role": "assistant", "content": answer})
            self.save_history()

            return answer

        except Exception as e:
            return f"❌ Hata oluştu: {str(e)}"
