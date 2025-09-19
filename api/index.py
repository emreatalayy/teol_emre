from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder='../templates', static_folder='../static')
CORS(app)

# Configure Gemini AI
API_KEY = os.getenv('GEMINI_API_KEY')
if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print(f"📊 Kullanılan API Anahtarı: {API_KEY[:20]}...")
else:
    model = None
    print("⚠️ GEMINI_API_KEY bulunamadı!")

def handler(request):
    if request.method == 'GET':
        if request.path == '/':
            return render_template('index.html')
        elif request.path == '/api/status':
            return jsonify({"status": "online", "model": "gemini-1.5-flash"})
    
    elif request.method == 'POST' and request.path == '/api/chat':
        try:
            data = request.get_json()
            user_message = data.get('message', '')
            
            if not user_message:
                return jsonify({"error": "Mesaj boş olamaz"}), 400
            
            if not model:
                return jsonify({"error": "AI model yapılandırılmamış"}), 500
            
            # System prompt for TEOL
            system_prompt = """Sen TEOL Dil Okulları'nın AI asistanısın. TEOL, 2013 ve 2014 yıllarında Türkiye ve Avrupa'nın en kaliteli dil okulu seçilmiş ve 2014 yılında dünya çapında en iyi dil okulu unvanını kazanmıştır. 

TEOL hakkında bilgiler:
- Türkiye'de 14 şube: Adana, Ankara, Bursa, Bodrum, Eskişehir, Erzurum, Fethiye, Giresun, İzmir, İzmit, İstanbul Avrupa, İstanbul Anadolu, Mersin, Rize, Sakarya, Samsun, Trabzon
- İngiltere'de 1 şube
- Modern eğitim yöntemleri
- Öğrenci odaklı yaklaşım
- Özelleştirilmiş öğrenme süreci
- Güçlü öğretim kadrosu
- Yenilikçi öğretim materyalleri

Sen samimi, yardımsever ve profesyonel bir asistansın. Dil öğrenimi, kurslar, TEOL hizmetleri hakkında bilgi veriyorsun. Türkçe konuşuyorsun ve gerektiğinde emoji kullanabilirsin."""
            
            # Generate response
            full_prompt = f"{system_prompt}\n\nKullanıcı: {user_message}\nAsistan:"
            response = model.generate_content(full_prompt)
            
            return jsonify({"response": response.text})
            
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
            return jsonify({"error": "Bir hata oluştu"}), 500
    
    return jsonify({"error": "Method not allowed"}), 405