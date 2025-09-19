from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
import os
import json
import time
import random
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Gemini API konfigürasyonu
# API anahtarınızı buraya direkt yazın veya environment variable olarak ayarlayın
API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyBG4K4ZgirpB1GpQ7FjVNDjYTDuXiwHEUQ')
print(f"📊 Kullanılan API Anahtarı: {API_KEY[:20]}...")  # İlk 20 karakteri göster
genai.configure(api_key=API_KEY)

# Model konfigürasyonu
# Kullanılacak model adını environment değişkeninden al veya varsayılan olarak
# ListModels çıktısına göre desteklenen bir model seçin (ör. models/gemini-1.5-pro)
MODEL_NAME = os.getenv('GEMINI_MODEL', 'models/gemini-2.0-flash')
model = genai.GenerativeModel(MODEL_NAME)

# Konuşma geçmişi ve sistem promptu
chat_history = []
SYSTEM_PROMPT = """
You are a very helpful, intelligent and friendly AI assistant.
You communicate with users naturally and always respond in English.
Try to give short and concise answers but you can go into detail when necessary.
Don't use emojis.
Always be polite and professional.
"""

class ChatBot:
    def __init__(self):
        self.conversation_history = []
        
    def generate_response(self, user_message, custom_prompt=None):
        # Build the full prompt
        if custom_prompt:
            full_prompt = f"{custom_prompt}\n\nKullanıcı mesajı: {user_message}"
        else:
            full_prompt = f"{SYSTEM_PROMPT}\n\nKullanıcı mesajı: {user_message}"

        max_retries = 5
        base_delay = 1.5  # seconds

        for attempt in range(1, max_retries + 1):
            try:
                # Gemini ile konuşma
                response = model.generate_content(full_prompt)

                # Konuşma geçmişine ekle
                assistant_text = getattr(response, 'text', None) or (
                    response.candidates[0].content.parts[0].text if getattr(response, 'candidates', None) else str(response)
                )

                self.conversation_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'user': user_message,
                    'assistant': assistant_text,
                    'custom_prompt': custom_prompt is not None
                })

                return {
                    'success': True,
                    'response': assistant_text,
                    'timestamp': datetime.now().isoformat()
                }

            except Exception as e:
                err_str = str(e)
                # If quota / rate-limit error, retry with exponential backoff + jitter
                if '429' in err_str or 'quota' in err_str.lower() or 'rate limit' in err_str.lower():
                    if attempt == max_retries:
                        return {
                            'success': False,
                            'error': 'Quota exceeded or rate limited after retries. ' + err_str,
                            'response': 'Üzgünüm, şu an API kotası aşıldı. Lütfen bir süre sonra tekrar deneyin veya planınızı/billing ayarlarınızı kontrol edin.',
                            'timestamp': datetime.now().isoformat()
                        }

                    # backoff with jitter
                    delay = base_delay * (2 ** (attempt - 1))
                    delay = delay + random.uniform(0, 1)
                    time.sleep(delay)
                    continue
                # Non-retriable error — return immediately
                return {
                    'success': False,
                    'error': err_str,
                    'response': 'Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.',
                    'timestamp': datetime.now().isoformat()
                }

# ChatBot instance
chatbot = ChatBot()

@app.route('/')
def index():
    try:
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Template dosyası bulunamadı. templates/index.html dosyasının olduğundan emin olun."

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'error': 'Mesaj gerekli'}), 400
    
    user_message = data['message']
    custom_prompt = data.get('custom_prompt', None)
    
    result = chatbot.generate_response(user_message, custom_prompt)
    
    return jsonify(result)

@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify({
        'history': chatbot.conversation_history[-20:],  # Son 20 mesaj
        'total_messages': len(chatbot.conversation_history)
    })

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    chatbot.conversation_history.clear()
    return jsonify({'success': True, 'message': 'Konuşma geçmişi temizlendi'})

@app.route('/api/set-system-prompt', methods=['POST'])
def set_system_prompt():
    global SYSTEM_PROMPT
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({'error': 'Prompt gerekli'}), 400
    
    SYSTEM_PROMPT = data['prompt']
    
    return jsonify({
        'success': True, 
        'message': 'Sistem promptu güncellendi',
        'new_prompt': SYSTEM_PROMPT
    })

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'online',
    'model': MODEL_NAME,
        'api_configured': API_KEY != 'AIzaSyDbM3AAFaVFEw9GVOdtSn2c4Pge_L80lXc',
        'conversation_count': len(chatbot.conversation_history),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Templates klasörü oluştur
    os.makedirs('templates', exist_ok=True)

    print("TEOL AI Asistan Flask Sunucusu Başlatılıyor...")
    print("API Endpoint: http://localhost:5000/api/chat")
    print("Web Arayüzü: http://localhost:5000")
    print("API Anahtarı Durumu:", "✅ Yapılandırıldı" if API_KEY != 'your-api-key-here' else "❌ Yapılandırılmadı")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
