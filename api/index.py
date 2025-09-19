from http.server import BaseHTTPRequestHandler
import json
import google.generativeai as genai
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Status endpoint
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_data = json.dumps({
            "status": "online",
            "message": "TEOL AI Asistan API çalışıyor",
            "version": "1.0.0"
        }, ensure_ascii=False)
        
        self.wfile.write(response_data.encode('utf-8'))
    
    def do_POST(self):
        try:
            # Configure Gemini AI
            API_KEY = os.getenv('GEMINI_API_KEY')
            if not API_KEY:
                self.send_error(500, "API key not configured")
                return
            
            genai.configure(api_key=API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Read request data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            user_message = data.get('message', '')
            if not user_message:
                self.send_error(400, "Message cannot be empty")
                return
            
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
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            response_data = json.dumps({"response": response.text}, ensure_ascii=False)
            self.wfile.write(response_data.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()