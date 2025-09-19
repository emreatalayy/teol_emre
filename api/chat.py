from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini AI
API_KEY = os.getenv('GEMINI_API_KEY')
if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

def handler(request):
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
        return jsonify({"error": "Bir hata oluştu"}), 500